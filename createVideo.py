# -*- coding: utf-8 -*- 

from manim import *
from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips
import os
from datetime import datetime

from googleapiclient.http import MediaFileUpload
from auth import get_drive_service

#PATH For Sources
PATH_BG_IMAGE_ANSWER= "./source/bg_image_answer.png"
PATH_BG_IMAGE_QUESTION= "./source/bg_image_question.png"
PATH_BG_IMAGE_INTRO= "./source/intro_fade.png"
PATH_BG_IMAGE_OUTRO= "./source/outro_fade.png"
PATH_VIDEO_INTRO= "./source/intro.mp4"
PATH_VIDEO_OUTRO= "./source/outro.mp4"
PATH_BG_SOUND= "./source/bg_sound.mp3"
PATH_FILE_QA=  "./source/question_answer.txt"
PATH_MANIM_DEFAULT_OUTPUT= "./media/videos/1080p60/MyScene.mp4"
MAX_WORD_PER_LINE = 30

class MyScene(Scene):

    def __init__(self, question, answer):
        super().__init__()
        self.questionA = question
        self.answerA = answer

    def construct(self):
        #Include sources and objects
        bg_image_question = ImageMobject(PATH_BG_IMAGE_QUESTION)
        bg_image_answer = ImageMobject(PATH_BG_IMAGE_ANSWER)
        bg_image_intro_fade = ImageMobject(PATH_BG_IMAGE_INTRO)
        bg_image_outro_fade =  ImageMobject(PATH_BG_IMAGE_OUTRO)
        text_h1_question = Text("QUESTION",
                                width= bg_image_answer.width-10, 
                                font_size= 120, 
                                weight=BOLD).to_edge(UP, buff= 1)
        text_h1_answer = Text("ANSWER", 
                              width= bg_image_question.width-10, 
                              font_size= 120, 
                              weight=BOLD).to_edge(UP, buff= 1)

        #Animation
        self.add(bg_image_intro_fade)
        self.play(Transform(bg_image_intro_fade, bg_image_question))
        self.play(Write(text_h1_question))

        #seperate by sentence section
        for question in self.questionA:
            hold_sec = len(question)
            print(hold_sec)
            paragraph_question = Paragraph(question,
                                       font_size=250,
                                       width=bg_image_question.width-5,
                                       slant=ITALIC)
            rectangle_question = RoundedRectangle(width= paragraph_question.width+1, height= paragraph_question.height+1)
            self.play(Create(rectangle_question))
            self.play(Write(paragraph_question))
            self.wait(hold_sec/12)
            self.play(FadeOut(paragraph_question))
            self.play(Uncreate(rectangle_question), run_time = 0.3)
        
        self.play(FadeOut(text_h1_question))
        self.play(Transform(bg_image_question, bg_image_answer), run_time=0.3)
        self.play(Write(text_h1_answer))

        for answer in self.answerA:
            hold_sec = len(question)
            paragraph_answer = Paragraph(answer,
                                     font_size=250,
                                     width=bg_image_answer.width-5)
        
            rectangle_answer = RoundedRectangle(width = paragraph_answer.width+1, height= paragraph_answer.height+1)

            self.play(Create(rectangle_answer))
            self.play(Write(paragraph_answer))
            self.wait(hold_sec/12)
            self.play(FadeOut(paragraph_answer))
            self.play(Uncreate(rectangle_answer), run_time= 0.3)
        
        
        self.play(FadeOut(text_h1_answer))
        self.play(Transform(bg_image_answer, bg_image_outro_fade))

class Main:

    def concatIntroOutro(id, output_folder_name):
    
        intro_clip = VideoFileClip(PATH_VIDEO_INTRO)
        manim_clip = VideoFileClip(PATH_MANIM_DEFAULT_OUTPUT)
        outro_clip = VideoFileClip(PATH_VIDEO_OUTRO)
        audio = AudioFileClip(PATH_BG_SOUND)

        final_clip = concatenate_videoclips([intro_clip, manim_clip, outro_clip])
        final_clip.audio = audio
        final_clip = final_clip.subclipped(0, final_clip.duration)
        final_clip.write_videofile(f"./output/{output_folder_name}/video{id}.mp4", codec="libx264", fps=30)
        print("Video has been created.")
   
    def createFolder():
        current_time = datetime.now().strftime("%y%m%d%H%M%S")
        output_folder_name = current_time
        if not os.path.exists(output_folder_name):
            os.makedirs(f"output/{output_folder_name}")
            
        return output_folder_name
    
    def upload_video(video_path, folder_id=None):
        service = get_drive_service()

        file_metadata = {"name": os.path.basename(video_path)}
        if folder_id:
            file_metadata["parents"] = [folder_id]

        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        print(f"✅ Video Has Been Uploaded. File ID: {file.get('id')}")
        return file.get("id")
      

    #RUN
    qa_file = open(PATH_FILE_QA, "r", encoding="utf-8")
    output_folder_name = createFolder()
    video_id = 1

    for qa in qa_file.readlines():
        questionCA = qa.split("::")[0].split(" ")
        answerCA = qa.split("::")[1].split(" ")

        questionA = []
        index = 0
        count = 0
        for word in questionCA:
            if count == 0:
                questionA.append(word)
            else:
                questionA[index] += " " + word

            count += 1
            if count >= MAX_WORD_PER_LINE:
                index += 1
                count = 0

        answerA = []
        index = 0
        count = 0
        for word in answerCA:
            if count == 0:
                answerA.append(word)
            else:
                answerA[index] += " " + word

            count += 1
            if count >= MAX_WORD_PER_LINE:
                index += 1
                count = 0
        
        scene = MyScene(questionA, answerA)
        scene.render()
        concatIntroOutro(video_id, output_folder_name)
        upload_video(f"./output/{output_folder_name}/video{video_id}.mp4")
        video_id += 1

    
    print(f"{video_id-1} Video has been created to ./output/{output_folder_name} and uploaded to the drive.")

    

if __name__ == "__main__":
    Main()
