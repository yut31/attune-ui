"""Train and evaluate EEGNet on a declared, participant-held-out driving pilot."""
import copy
import json
from pathlib import Path
import random
import time

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (classification_report, confusion_matrix, f1_score,
                             balanced_accuracy_score, roc_auc_score, average_precision_score)

from nova2026.architecture.cnn import EEGNet
from nova2026.architecture.lossfun import FocalLoss
from nova2026.training_feedback import write_json

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'base/datasets/driving-attention'
OUT = ROOT / 'training-runs/driving-pilot-20260910'
SEED = 42


def metrics(y, probability):
    prediction=(probability>=.5).astype(int)
    result={'macro_f1':float(f1_score(y,prediction,labels=[0,1],average='macro',zero_division=0)),
            'balanced_accuracy':float(balanced_accuracy_score(y,prediction)),
            'confusion_matrix':confusion_matrix(y,prediction,labels=[0,1]).tolist(),
            'classification_report':classification_report(y,prediction,labels=[0,1],
                target_names=['usual_response','slowest_session_decile'],output_dict=True,zero_division=0)}
    if len(np.unique(y))==2:
        result.update(roc_auc=float(roc_auc_score(y,probability)),
                      average_precision=float(average_precision_score(y,probability)))
    return result


def evaluate(model, x, y, criterion):
    model.eval()
    with torch.inference_mode():
        logits=model(x)
        return float(criterion(logits,y)),logits.softmax(1)[:,1].numpy()


def main():
    torch.set_num_threads(2);torch.manual_seed(SEED);np.random.seed(SEED);random.seed(SEED)
    manifest=json.loads((DATA/'manifest.json').read_text())
    subjects=sorted({f['name'].split('_')[0] for f in manifest['files']})
    missing=[s for s in subjects if not (DATA/'prepared'/f'{s}.npz').exists()]
    if missing:raise ValueError(f'Preprocessing incomplete: {missing}')
    order=np.random.default_rng(SEED).permutation(subjects).tolist()
    split={'train':order[:17],'validation':order[17:22],'test':order[22:]}
    OUT.mkdir(parents=True,exist_ok=False)
    write_json(OUT/'split.json',split)
    arrays={};channels=None
    for role,people in split.items():
        xx=[];yy=[];ids=[]
        for subject in people:
            with np.load(DATA/'prepared'/f'{subject}.npz',allow_pickle=False) as item:
                names=item['channels'].tolist()
                if channels is None:channels=names
                if names!=channels:raise ValueError('Electrode order differs across recordings')
                xx.append(item['data']);yy.append(item['labels']);ids.extend([subject]*len(item['labels']))
        arrays[role]=[np.concatenate(xx),np.concatenate(yy),ids]
    mean=arrays['train'][0].mean(axis=(0,2),keepdims=True)
    std=arrays['train'][0].std(axis=(0,2),keepdims=True).clip(min=1e-6)
    for role,(x,y,ids) in arrays.items():
        arrays[role]=[torch.from_numpy(((x-mean)/std).astype(np.float32)),torch.from_numpy(y).long(),ids]
    x,y,_=arrays['train'];xv,yv,_=arrays['validation'];xt,yt,test_ids=arrays['test']
    print({k:{'windows':len(v[1]),'slow_responses':int(v[1].sum())} for k,v in arrays.items()},flush=True)
    model=EEGNet(chn=len(channels))
    optimizer=torch.optim.Adam(model.parameters(),lr=1e-3)
    criterion=FocalLoss(gamma=2,alpha=[1,3.5])
    generator=torch.Generator().manual_seed(SEED)
    loader=DataLoader(TensorDataset(x,y),batch_size=32,shuffle=True,generator=generator)
    best_score=-1.;best_state=None;best_epoch=0;history=[];started=time.perf_counter()
    # Only validation subjects select an epoch. Test subjects are evaluated once.
    for epoch in range(1,31):
        model.train();loss_sum=0.
        for xb,yb in loader:
            optimizer.zero_grad(set_to_none=True)
            logits=model(xb);loss=criterion(logits,yb);loss.backward();optimizer.step()
            loss_sum+=loss.item()*len(yb)
        val_loss,prob=evaluate(model,xv,yv,criterion)
        score=f1_score(yv.numpy(),prob>=.5,labels=[0,1],average='macro',zero_division=0)
        row={'epoch':epoch,'train_loss':loss_sum/len(y),'validation_loss':val_loss,
             'validation_macro_f1':float(score),'elapsed_s':time.perf_counter()-started}
        history.append(row);write_json(OUT/'history.json',history)
        print(f'Epoch {epoch}/30 | loss {row["train_loss"]:.4f} | validation F1 {score:.3f} | {row["elapsed_s"]:.1f}s',flush=True)
        if score>best_score:
            best_score=score;best_epoch=epoch;best_state=copy.deepcopy(model.state_dict())
        if epoch-best_epoch>=6:
            print('Stopping after 6 epochs without validation-F1 improvement.',flush=True);break
    model.load_state_dict(best_state)
    _,test_probability=evaluate(model,xt,yt,criterion)
    test_metrics=metrics(yt.numpy(),test_probability)
    baseline=metrics(yt.numpy(),np.zeros(len(yt)))
    checkpoint={'format_version':1,'task':'driving_slow_response_pilot','architecture':'EEGNet',
        'state_dict':best_state,'channels':channels,'sample_rate':128,'samples':256,'units':'uV',
        'preprocessing':'butterworth4_0.5_45Hz_6s_prestimulus_resample128_last2s',
        'training_mean':torch.from_numpy(mean),'training_std':torch.from_numpy(std),
        'classes':['usual_response','slowest_session_decile'],'best_epoch':best_epoch,
        'source':manifest['source'],'split':split}
    torch.save(checkpoint,OUT/'model.pt')
    reloaded=EEGNet(chn=len(channels));reloaded.load_state_dict(torch.load(OUT/'model.pt',weights_only=True)['state_dict']);reloaded.eval()
    with torch.inference_mode():
        np.testing.assert_allclose(reloaded(xt[:2]).numpy(),model(xt[:2]).numpy(),rtol=1e-5,atol=1e-6)
    np.savez_compressed(OUT/'heldout_predictions.npz',subject=test_ids,target=yt.numpy(),probability=test_probability)
    report={'dataset':manifest['source'],'source_license':'CC BY 4.0','seed':SEED,
        'sampling':'First filename per subject; uniform seed-based sample of up to 40 eligible trials per recording',
        'split':split,'counts':{k:{'windows':len(v[1]),'positive':int(v[1].sum())} for k,v in arrays.items()},
        'best_epoch':best_epoch,'epochs_run':len(history),'training_seconds':time.perf_counter()-started,
        'test':test_metrics,'always_usual_response_baseline':baseline,
        'test_by_subject':{person:metrics(yt.numpy()[np.array(test_ids)==person],test_probability[np.array(test_ids)==person]) for person in split['test']},
        'versions':{'torch':torch.__version__,'numpy':np.__version__},
        'limitations':['Pilot sample, not a full-dataset benchmark','Steering-response labels, not PVT or auditory-attention labels',
          '30 scalp channels (two references excluded), not the original 62-channel model','Not evaluated on the buildathon headset',
          'Test people excluded from training, normalization, and epoch selection','Scores are not calibrated probabilities of attention lapses']}
    write_json(OUT/'report.json',report)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    axes[0].plot([r['epoch'] for r in history],[r['train_loss'] for r in history],label='Train')
    axes[0].plot([r['epoch'] for r in history],[r['validation_loss'] for r in history],label='Validation')
    axes[0].set(xlabel='Epoch',ylabel='Focal loss',title='Learning curves');axes[0].legend()
    cm=np.array(test_metrics['confusion_matrix']);axes[1].imshow(cm,cmap='Blues')
    for i in range(2):
        for j in range(2):axes[1].text(j,i,str(cm[i,j]),ha='center',va='center')
    axes[1].set(xticks=[0,1],yticks=[0,1],xticklabels=['Usual','Slow'],yticklabels=['Usual','Slow'],
                xlabel='Predicted',ylabel='Actual',title='Held-out people')
    fig.tight_layout();fig.savefig(OUT/'training_results.png',dpi=160);plt.close(fig)
    print(json.dumps({'output':str(OUT),'test_macro_f1':test_metrics['macro_f1'],
          'baseline_macro_f1':baseline['macro_f1'],'best_epoch':best_epoch},indent=2),flush=True)


if __name__=='__main__':main()
