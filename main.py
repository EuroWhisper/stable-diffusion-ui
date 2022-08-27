from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from pydantic import BaseModel

import json
import uuid
import requests
from os import path

LOCAL_SERVER_URL = 'http://stability-ai:5000'
PREDICT_URL = LOCAL_SERVER_URL + '/predictions'

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# defaults from https://huggingface.co/blog/stable_diffusion
class ImageRequest(BaseModel):
    prompt: str
    num_outputs: str = "1"
    num_inference_steps: str = "50"
    guidance_scale: str = "7.5"
    width: str = "512"
    height: str = "512"
    seed: str = "30000"

def save_prompt(prompt):
    historyObj = {
        'prompt': prompt['prompt'],
        'num_outputs': prompt['num_outputs'],
        'num_inference_steps': prompt['num_inference_steps'],
        'guidance_scale': prompt['guidance_scale'],
        'width': prompt['width'],
        'height': prompt['height'],
        'seed': prompt['seed'],
        'id': str(uuid.uuid4())
    }
    promptHistoryFilename = 'prompt-history.json'

    if path.isfile(promptHistoryFilename) is False:
        with open(promptHistoryFilename, 'w') as json_file:
            json.dump([], json_file,indent=4); 
    
    listObj = []
    # append data to json file
    with open(promptHistoryFilename) as infile:
        listObj = json.load(infile)
        
    listObj.append(historyObj)

    with open(promptHistoryFilename, 'w') as json_file:
        json.dump(listObj, json_file, 
        indent=4,  
        separators=(',',': '))

@app.get('/')
def read_root():
    return FileResponse('index.html')

@app.get('/ping')
async def ping():
    try:
        requests.get(LOCAL_SERVER_URL)
        return {'OK'}
    except:
        return {'ERROR'}

@app.post('/image')
async def image(req : ImageRequest):
    data = {
        "input": {
            "prompt": req.prompt,
            "num_outputs": req.num_outputs,
            "num_inference_steps": req.num_inference_steps,
            "width": req.width,
            "height": req.height,
            "seed": req.seed,
            "guidance_scale": req.guidance_scale,
        }
    }

    

    save_prompt(data['input'])

    if req.seed == "-1":
        del data['input']['seed']

    res = requests.post(PREDICT_URL, json=data)
    return res.json()

@app.get('/media/ding.mp3')
def read_root():
    return FileResponse('media/ding.mp3')
