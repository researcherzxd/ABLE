from mlp_model import MLP
from dataset import trafficSet
from utils import *
import torch, time, os, shutil
import numpy as np
import pandas as pd
#from tensorboard_logger import Logger
from torch import nn, optim
from torch.utils.data import DataLoader
import os
from proxy_config import proxy_args
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

torch.manual_seed(41)
torch.cuda.manual_seed(41)

def train_epoch(model, optimizer, criterion, train_dataloader, show_interval=10):
    model.train()
    print("start_training")
    mse_meter, loss_meter, it_count = 0, 0, 0
    for inputs, target in train_dataloader:
        inputs = inputs.to(device)
        target = target.to(device)
        # zero the parameter gradients
        optimizer.zero_grad()
        # forward
        output = model(inputs)
        output = output.to(torch.float32)
        target = target.to(torch.float32)
        # print(target.shape)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        loss_meter += loss.item()
        it_count += 1
        mse = cal_mean_error(target, output)
        mse_meter += mse
        if it_count != 0 and it_count % show_interval == 0:
            print("%d,loss:%.3e mse:%.3f" % (it_count, loss.item(), mse))
    return loss_meter / it_count, mse_meter / it_count


def val_epoch(model, criterion, val_dataloader, threshold=0.5):
    model.eval()
    mse_meter,loss_meter, it_count = 0, 0, 0
    with torch.no_grad():
        for inputs, target in val_dataloader:
            inputs = inputs.to(device)
            target = target.to(device)
            output = model(inputs)
            loss = criterion(output, target)
            loss_meter += loss.item()
            it_count += 1
            mse = cal_mean_error(target, output)
            mse_meter += mse
    return loss_meter / it_count, mse_meter / it_count


def train(proxy_args):
    
    # data
    train_dataset = trafficSet(path = proxy_args.train_data_path,train=True)
    train_dataloader = DataLoader(train_dataset, batch_size=proxy_args.batch_size, shuffle=True)
    val_dataset = trafficSet(path = proxy_args.train_data_path,train=False)
    val_dataloader = DataLoader(val_dataset, batch_size=proxy_args.batch_size)
    print("train_datasize", len(train_dataset), "val_datasize", len(val_dataset))
    # get model 
    print(train_dataset.num_tokens)
    print(train_dataset.max_len)
    print(train_dataset.num_tokens)
    
    model =  MLP(num_tokens=train_dataset.num_tokens,
                                num_outputs=1,
                                num_hid=proxy_args.num_hid,
                                num_layers=proxy_args.num_layers, # TODO: add these as hyperparameters?
                                dropout=0.1,
                                max_len=train_dataset.max_len)
#     if args.ckpt and not args.resume:
#         state = torch.load(args.ckpt, map_location='cpu')
#         model.load_state_dict(state['state_dict'])
#         print('train with pretrained weight val_f1', state['f1'])
    model = model.to(device)
    print(model)
    # optimizer and loss
    optimizer = optim.Adam(model.parameters(), lr=proxy_args.lr)
    criterion = nn.MSELoss()
    # model save dir
    model_save_dir = '%s/%s' % (proxy_args.ckpt, proxy_args.model_name,)
    mkdirs(model_save_dir)
    best_mse = 100
    lr = proxy_args.lr
    start_epoch = 1
    stage = 1
    # train from last save point
#     if args.resume:
#         if os.path.exists(args.ckpt):  # weight path
#             model_save_dir = args.ckpt
#             current_w = torch.load(os.path.join(args.ckpt, config.current_w))
#             best_w = torch.load(os.path.join(model_save_dir, config.best_w))
#             best_f1 = best_w['loss']
#             start_epoch = current_w['epoch'] + 1
#             lr = current_w['lr']
#             stage = current_w['stage']
#             model.load_state_dict(current_w['state_dict'])
#             if start_epoch - 1 in config.stage_epoch:
#                 stage += 1
#                 lr /= config.lr_decay
#                 utils.adjust_learning_rate(optimizer, lr)
#                 model.load_state_dict(best_w['state_dict'])
#             print("=> loaded checkpoint (epoch {})".format(start_epoch - 1))
#     logger = Logger(logdir=model_save_dir, flush_secs=2)
    # =========>start training<=========
    for epoch in range(start_epoch, proxy_args.max_epoch + 1):
        since = time.time()
        train_loss, train_mse = train_epoch(model, optimizer, criterion, train_dataloader, show_interval=100)
        val_loss, val_mse = val_epoch(model, criterion, val_dataloader)
        print('#epoch:%02d stage:%d train_loss:%.3e train_mse:%.3f  val_loss:%0.3e val_mse:%.3f time:%s\n'
              % (epoch, stage, train_loss, train_mse, val_loss, val_mse, print_time_cost(since)))
        # logger.log_value('train_loss', train_loss, step=epoch)
        # logger.log_value('train_f1', train_f1, step=epoch)
        # logger.log_value('val_loss', val_loss, step=epoch)
        # logger.log_value('val_f1', val_f1, step=epoch)
        state = {"state_dict": model.state_dict(), "epoch": epoch, "loss": val_loss, 'mse': val_mse, 'lr': lr,
                 'stage': stage}
        save_ckpt(state, best_mse > val_mse, model_save_dir)
        best_mse = min(best_mse, val_mse)
        print(best_mse)
        if epoch in proxy_args.stage_epoch:
            stage += 1
            lr /= proxy_args.lr_decay
            best_w = os.path.join(model_save_dir, proxy_args.best_w)
            model.load_state_dict(torch.load(best_w)['state_dict'])
            print("*" * 10, "step into stage%02d lr %.3ef" % (stage, lr))
            adjust_learning_rate(optimizer, lr)
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, help="the path of train_data")
    command_args = parser.parse_args()
    proxy_args.train_data_path = command_args.data_path
    train(proxy_args)