from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from google import genai
import PIL.Image as Img
import os
import json
from dotenv import load_dotenv
from pathlib import Path
import logging
from wand.image import Image
from wand.color import Color

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env_path = '.env' 
load_dotenv(dotenv_path=env_path)

async def image_processing(file_path):
    try:
        image = Img.open(file_path)
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        response = client.models.generate_content( model="gemini-2.0-flash",
            contents=["verify image is that doha residency permit, if it is not doha residency don't give output,\
                        if it is provide data in this json format ''' idNo dob, expiry, nationalityEng, nationalityAra,\
                        occupation, nameEng, name_ar, passportNumber, \
                    passportExpiry, serialNo, residencyType, employer''' ", image])
        
        if response.text:
            json_str = response.text.strip().strip('```json').strip('```').strip()
            data_dict = json.loads(json_str)
            return data_dict    
    except Exception as e:
             print('image processing error',e)

async def process_pdf(data_file_path: Path):
    try:
        output_file_path = f"images/{data_file_path.stem}.png"

        with Image(filename=str(data_file_path), resolution=300) as img:
            img.background_color = Color("white")
            img.alpha_channel = 'remove'
            img.save(filename=output_file_path)
        results = await image_processing(output_file_path)      
        return results
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        return None

async def process_upload_file(request: Request):
    temp_file_path = None
    try:
        form = await request.form()
        uploaded_file = form.get('file')
        
        if not uploaded_file or not hasattr(uploaded_file, "filename"):
            raise HTTPException(status_code=400, detail="No valid file uploaded")
        
        images_dir = Path("images")
        images_dir.mkdir(exist_ok=True)
        
        temp_file_path = images_dir / uploaded_file.filename
        logger.info(f"Saving file to: {temp_file_path}")
 
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await uploaded_file.read())
        
        if temp_file_path.suffix.lower() == '.pdf':
            logger.info("Processing PDF")
            processed_data = await process_pdf(temp_file_path)
        else:
            logger.info("Processing image file")
            processed_data = await image_processing(temp_file_path)
        
        if not processed_data:
            return {"message": "Please upload a valid residency permit", "messageType": "E"}
        
        return {"message": "Success", "messageType": "S", "response": processed_data}
    
    except Exception as e:
        print(e)
        return JSONResponse(status_code = 500, content = {"message": "Internal Server Error"})  
    
    finally:
         if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        






        
