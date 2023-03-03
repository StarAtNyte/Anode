#from setup import chatbot
from pdf import PDF
import streamlit as st
import textwrap
import replicate
import os
from PyPDF2 import PdfMerger
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import openai

openai.api_key = "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"

# Environment Variable for Replicate
os.environ["REPLICATE_API_TOKEN"] = "b3ea4715f5e3450de2093c2c82fd224208a069e3"

stability_api = client.StabilityInference(
    key='sk-FMO2lOKk4jwqehIGpDxfnxFt5ctfkKWcEtaZCXMxiKC1UmKT',
    verbose=True,
)
# PDF Object
pdf = PDF()
cover_pdf = PDF()
foreword_pdf = PDF()
summary_pdf = PDF()



st.title('Create A Illustrated Novel From a simple Title')
st.image("https://imageio.forbes.com/blogs-images/bernardmarr/files/2019/03/AdobeStock_235115918-1200x800.jpeg?format=jpg&width=1200")
st.text('''
Please follow the following instructions:
1. Press all the buttons in order.
2. Press the next button only after previous task gets completed.
3. Download button will appear after everything is completed.
4. We recommend 3 chapters for optimal result.
4. If any error occurs, please press the button of the same step in which the error occured.

                    Thank you.
''')



# Text Boxes
title = st.text_input('Title of the book')
author = st.text_input('Author of the book')

# Stable Diffusion
model_id = "stabilityai/stable-diffusion-2-1"


cover_pdf.add_page()
#Cover page image
if st.button('Get Cover Image'):
    
    
    answers = stability_api.generate(
        prompt= f"Minima book Illustration, ({title}), (story of {title})",
        width=768, # Generation width, defaults to 512 if not included.
        height=1088,
    )
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                img_name = str(artifact.seed)+ ".png"
                img.save(img_name)
                image = Image.open(img_name)
                
                # Custom font style and font size
                W = 768
                title_font = ImageFont.truetype('playfair/playfair-font.ttf', 50)
                author_font = ImageFont.truetype('playfair/playfair-font.ttf', 20)
                title_text = f"{title}"
                image_editable = ImageDraw.Draw(image)
                w, h = image_editable.textsize(title)
                image_editable.text(((W-w)/3.5,50), title_text, (237, 230, 211), font=title_font)
                image_editable.text((630,1050), author, (237, 230, 211), font=author_font,align='left')
                image.save("cover.jpg")
                
                cover_pdf.image("cover.jpg",x=0, y=0, w= 210, h= 297)

                cover_pdf.output('cover.pdf', 'F')
                st.image("cover.jpg")

# Number of chapters
chapters = st.number_input('Enter Number of chapters.', min_value=1, max_value=100, value=2, step=1)

## PDF Body
if st.button('Get PDF'):
    st.write('Processing')

    text = []
    response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=f"Generate {chapters} chapter titles for the novel {title}",
                    max_tokens = 100,
                    temperature=0.6
                )
    #response = chatbot.ask(f"Generate 10 chapter titles for the novel {title}")
    #chaps= response['message'].rsplit("\n")
    chaps = response['choices'][0]['text'].rsplit('\n')
    chaps = [chap for chap in chaps if chap != '']
    print(chaps)
    

    for i in range(1,chapters+1):
        #response = chatbot.ask(f"generate content for chapter {i}")
        response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"generate content for chapter {i} :{chaps[i-1][4:-1]} of the novel titled {title}",
                max_tokens = 300,
                temperature=0.6
            )
        text.append(response['choices'][0]['text'])

    # Text to TXT
    for i in range(0, chapters):
        with open (f'chapter{i+1}.txt', 'w') as file:  
            file.write(text[i])  
    


    pdf.set_title(title)
    pdf.set_author(author)
    for i in range(1, chapters+1):
        answers = stability_api.generate(
        prompt= f"Minimal Illustration, ({chaps[i-1][4:-1]}) (Van Gogh)",
        width=768, # Generation width, defaults to 512 if not included.
        height=384,
        )
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img_name = str(artifact.seed)+ ".png"
                    img.save(img_name)
                    image = Image.open(img_name)
                
                # Custom font style and font size
                
                title_font = ImageFont.load_default()
                title_text = f"{title}"
                image_editable = ImageDraw.Draw(image)
                image_editable.text((15,15), title_text, (237, 230, 211), font=title_font)
                image.save(f"{chaps[i-1][4:-1]}.jpg")
                
        
        pdf.print_chapter(i, f"{chaps[i-1][4:-1]}", f'chapter{i}.txt')
        pdf.image(f"{chaps[i-1][4:-1]}.jpg",x= 10, w=190, h = 80)
    pdf.output('dummy.pdf', 'F')
    
    #cohere text summarization
    #response = co.generate( 
    #model='xlarge', 
    #prompt = complete_text,
    #max_tokens=250, 
    #temperature=0.9)

    #summary = response.generations[0].text
    #pdf of summary
    #with open (f'about_{title}.txt', 'w') as file:  
    #        file.write(f"About {title}\n\n{summary}")
    #summary_pdf.print_chapter(i, f"About_{title}", f'about_{title}.txt')
    #summary_pdf.output(f'about_{title}.pdf', 'F')
    
    #Foreword generation
    #foreword_response = chatbot.ask( f"write foreword for the book written by you on the title {title}, in the style of an experienced writer, 400 words")
    foreword_response = openai.Completion.create(
                model="text-davinci-003",
                prompt=f"write foreword for the book written by you on the title {title}, in the style of an experienced writer, 400 words",
                max_tokens = 300,
                temperature=0.6
            )
    foreword = "FOREWORD\n\n\n\n" + foreword_response['choices'][0]['text']
    
    with open (f'foreword.txt', 'w') as file:  
            file.write(foreword)
    foreword_pdf.print_chapter(i, f"Foreword", f'foreword.txt')
    foreword_pdf.output(f'foreword.pdf', 'F')

    # Merge pdfs
    pdfs = ['cover.pdf', 'foreword.pdf' ,'dummy.pdf']

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("result.pdf")
    merger.close()

    # Download Button
    with open("result.pdf", "rb") as file:
        btn=st.download_button(
        label="⬇️ Download PDF",
        data=file,
        file_name="mybook.pdf",
        mime="application/octet-stream"
    )



##if st.button('Get Audio Book'):
##    # pdf to audio
##    audio_model = replicate.models.get("afiaka87/tortoise-tts")
##    audio_version = audio_model.versions.get("e9658de4b325863c4fcdc12d94bb7c9b54cbfe351b7ca1b36860008172b91c71")
##    reader = PdfReader("dummy.pdf")
##    text = ""
##    for page in reader.pages:
##        text += page.extract_text() + "\n" 
##    output = audio_version.predict(text=text)
##    st.audio(output, format='audio/ogg')
