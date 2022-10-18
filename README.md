# Prerequisites
1. A computer powerful enogh for running Apollo+LGSVL-2021.1. 
(Or two computers: one for Apollo, one for LGSVL)
2. rtamt (evaluating robustness degree of an STL formula, please refer to [the github page](https://github.com/nickovic/rtamt))
3. python3
   ```bash
   sudo pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113
   sudo pip3 install websockets pandas sklearn tqdm
   ```

# Step by step

## Run Apollo with LGSVL
Please refer to [the detailed documentation](https://www.svlsimulator.com/docs/system-under-test/apollo-master-instructions/) for co-simulation of Apollo with LGSVL.
Set the LGSVL to API-Only mode.
Then, Install the customized map map/original_map/base_map.bin to Apollo with the [guide](https://github.com/lgsvl/apollo-5.0/tree/simulator/modules/map/data).

## Setup our bridge.
1. Download and go to the root. Note that the source code should be downloaded and set up on the computer running Apollo.
	```bash
	git clone https://github.com/researcherzxd/ABLE.git
	cd ABLE-SourceCode
	```
2. Install Python API to support for LGSVL-2021.1.
	```bash
	cd ABLE-SourceCode/bridge/PythonAPImaster
	pip3 install --user -e .  
	##If "pip3 install --user -e ." fail, try the following command:
	python3 -m pip install -r requirements.txt --user .
	```

3. Connect our bridge to the LGSVL and Apollo:
	Go the bridge in the folder:/ABLE-SourceCode/bridge
	```bash
	cd /ABLE/bridge
	```
	Find file: [bridge.py](ABLE-SourceCode/bridge/bridge.py).
	There is class `Server` in [bridge.py](ABLE-SourceCode/bridge/bridge.py). 

	Modify the `SIMULATOR_HOST` and `SIMULATOR_PORT` of `Server` to your IP and port of LGSVL.
	Modify the `BRIDGE_HOST` and `BRIDGE_PORT` of `Server` to your IP and port of Apollo.
	
4. Test the parser:
	If the support for parser is properly installed, we can test it by running:
	```bash
	cd /ABLE
	python3 monitor.py
	```
	If there is no errors and warnings, the parser is correct.


## Run our bridge.
Open a terminal on the computer running Apollo.
```bash
cd /ABLE/bridge
python3 bridge.py
```
Keep it Running.


## Run the Generation Algorithm.
Open another terminal on the computer running Apollo.
```bash
cd /ABLE
python3 GFN_Fuzzing.py
```
If the brige is set properly, you will see the LGSVL and Apollo running. The results will be put into a folder that you set in path_config.py.

