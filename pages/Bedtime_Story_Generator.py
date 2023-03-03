from setup import chatbot
from pdf import PDF
import requests
import streamlit as st
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



st.title('Generate Bedtime Stories')
st.text('''
Please follow the following instructions:
1. Press all the buttons in order.
2. Press the next button only after previous task gets completed.
3. Download button will appear after everything is completed.
4. We recommend 3 chapters for optimal result.
5. If any error occurs, please click the button of the step in which the error occured.

                    Thank you.
''')


# Text Boxes
title = st.text_input('Enter a title')
if title:
    st.session_state.title = title

moral = st.text_input('Enter a moral')
if moral:
    st.session_state.moral = moral

author = "BookAI"

# Stable Diffusion
model_id = "stabilityai/stable-diffusion-2-1"


cover_pdf.add_page()
#Cover page image
if st.button('Get Cover Image'):
    
    answers = stability_api.generate(
        prompt= f"Minima book Illustration of a children bedtime story, ({st.session_state.title})",
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
                title_font = ImageFont.truetype('playfair/playfair-font.ttf', 35)
                author_font = ImageFont.truetype('playfair/playfair-font.ttf', 20)
                title_text = f"{st.session_state.title}"
                words_in_title = title_text.split(' ')
                if ':' in title_text:
                    temp = title_text.split(':')
                    title_text = temp[0] + '\t\t\n' + temp[1]
                if len(words_in_title) >4:
                    title_text = words_in_title[0:4] + '\t\n' + words_in_title[4:]
                image_editable = ImageDraw.Draw(image)
                w, h = image_editable.textsize(st.session_state.title)
                image_editable.text(((W-w)/3.7,25), title_text, (237, 230, 211), font=title_font)
                image_editable.text((630,1050), author, (237, 230, 211), font=author_font,align='left')
                image.save("cover.jpg")
                
                cover_pdf.image("cover.jpg",x=0, y=0, w= 210, h= 297)

                cover_pdf.output('cover.pdf', 'F')
                st.image("cover.jpg")

# Number of chapters
paragraphs = st.number_input('Enter Number of paragraphs.', min_value=1, max_value=100, value=2, step=1)

complete_text =''
## PDF Body
completed = False
if st.button('Get PDF'):
    st.write('Writing Your Storyy.')
    st.markdown("![Writing Your Story](https://media.giphy.com/media/YAnpMSHcurJVS/giphy.gif)")

    text = []
    response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt= f"Generate {paragraphs} paragraph titles for the children bedtime story {st.session_state.title} with moral {st.session_state.moral}",
                    max_tokens = 100,
                    temperature=0.6
                )

    chaps = response['choices'][0]['text'].rsplit('\n')
    chaps = [chap for chap in chaps if chap != '']
    

    for i in range(1,paragraphs+1):
        response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt= f"generate a paragraph for paragraph {i-1}: {chaps[i-1]}",
                    max_tokens = 100,
                    temperature=0.6
                )
        if response['message'][0:2] == "In":
            response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt= f"generate a paragraph for paragraph {i}",
                    max_tokens = 100,
                    temperature=0.6
                )

        text.append(response['message'])
        complete_text += text[0]

    # Text to TXT
    for i in range(0, paragraphs):
        with open (f'chapter{i+1}.txt', 'w') as file:  
            file.write(text[i])  
    


    pdf.set_title(st.session_state.title)
    pdf.set_author(author)
    for i in range(1, paragraphs+1):
        answers = stability_api.generate(
        prompt= f"Generate an children storybook style image for paragraph titled: ({chaps[i-1][4:-1]})",
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
                title_text = f"{st.session_state.title}"
                image_editable = ImageDraw.Draw(image)
                image_editable.text((15,15), title_text, (237, 230, 211), font=title_font)
                image.save(f"{i-1}.jpg")
                
        pdf.print_chapter(i, f"{chaps[i-1][4:-1]}", f'chapter{i}.txt')
        pdf.image(f"{i-1}.jpg",x= 10, w=190, h = 80)
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


    # Merge pdfs
    pdfs = ['cover.pdf','dummy.pdf']

    merger = PdfMerger()

    for pdf in pdfs:
        merger.append(pdf)

    merger.write("result.pdf")
    merger.close()
    completed = True

# Download Button
if completed:
    with open("result.pdf", "rb") as file:
        btn=st.download_button(
        label="⬇️ Download PDF",
        data=file,
        file_name=f"{st.session_state.title}.pdf",
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
