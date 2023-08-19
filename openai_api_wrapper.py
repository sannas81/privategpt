from flask import Flask, jsonify, request
import torch
from transformers import pipeline


app = Flask(__name__)
nlp = pipeline('text2text-generation', model='facebook/blenderbot-400M') # example text generation model


@app.route('/v1/chat/completions', methods=['POST'])
def completions():
    try:
        data = request.get_json()
        
        message = str(data['message']).strip().replace('\r\n','').replace('\n',' ')

        if 'functions' in data:
            functions = [str(f).strip().lower() for f in data['functions']]

            function_calls = []
            
            for func in ['date', 'time']:
                if func in functions:
                    function_calls.append({'type':func})
                    
            if len(function_calls) == 0:
                raise ValueError("Invalid input")
                
            outputs = nlp([[message], function_calls])
            
            completion = ''.join([output[0]['generated_text'] for output in outputs]).split('<|im_sep|>')[1]
            
        else:
            temperature = float(data.get('temperature', 1))
            top_p = float(data.get('top_p', 1))
            n = int(data.get('n', 1))
            stream = bool(data.get('stream', False))
            stop = None
            max_tokens = int(data.get('max_tokens', -1))
            presence_penalty = float(data.get('presence_penalty', 0))
            frequency_penalty = float(data.get('frequency_penalty', 0))
            logit_bias = {}
            user = ''
            
            inputs = {'context':message}
            params = {k: v for k, v in locals().items()}
            del params['inputs'], params['outputs']
            result = self._generate(**params, **inputs)[0].get('generated_text')
            choice = {"completion":result,"index":0}
            choices=[choice]
        
    except Exception as e:
        return jsonify({"error":str(e)}), 500
    
    usage={'requests':{'count':1,'total':1}}

    response={
      "id":"some id",
      "object":"chat_completion",
      "created":int(round(float(datetime.now().timestamp()))*1000),
      "model":"facebook/blenderbot-400M" if not ('model' in data) else data["model"], 
      "choices":[
          {"completion":completion,"index":0},
      ],
      "usage":usage
  }
      
    return jsonify(response)
    
    
if __name__ == '__main__':
    app.run(debug=True)
