from PIL import Image, ImageDraw, ImageFont
import io
import os

def create_sample_image(text, width=800, height=400, bg_color=(99, 102, 241), text_color=(255, 255, 255)):
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 40)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill=text_color, font=font)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return img_io

def create_sample_audio(duration=5):
    import wave
    import struct
    import math

    sample_rate = 44100
    num_samples = sample_rate * duration

    with wave.open('sample_audio.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            frequency = 440 + (i / num_samples) * 220
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            wav_file.writeframes(struct.pack('<h', value))

    with open('sample_audio.wav', 'rb') as f:
        return f.read()

def create_sample_video(duration=3):
    import os
    script = """
    function CreateSampleVideo()
        % Create a simple video
        v = VideoWriter('sample_video.mp4');
        v.FrameRate = 30;
        open(v);

        for i = 1:30*duration
            img = zeros(400, 800, 3);
            color = [i/(30*duration), 0, 1-i/(30*duration)];
            img(:) = color;
            writeVideo(v, img);
        end

        close(v);
    end
    """
    return script.encode('utf-8')

if __name__ == '__main__':
    os.makedirs('assets', exist_ok=True)

    # Create sample images
    for i, (text, color) in enumerate([
        ('Математика: $f(x) = \sin(x)$', (99, 102, 241)),
        ('Физика: $E = mc^2$', (16, 185, 129)),
        ('Химия: $H_2O$', (245, 158, 11)),
        ('История: 1917 год', (239, 68, 68)),
        ('География: Москва', (34, 197, 94))
    ]):
        img = create_sample_image(text, width=800, height=400, bg_color=color)
        with open(f'assets/math_img_{i+1}.png', 'wb') as f:
            f.write(img.getvalue())
        print(f'Created: math_img_{i+1}.png')

    # Create sample audio (Python + wave)
    try:
        audio_data = create_sample_audio(5)
        with open('assets/sample_lecture.wav', 'wb') as f:
            f.write(audio_data)
        print('Created: sample_lecture.wav')
    except Exception as e:
        print(f'Could not create audio: {e}')

    # Create simple text file for file upload question
    with open('assets/sample_answer.txt', 'w', encoding='utf-8') as f:
        f.write('Это пример ответа на вопрос по математике.\n\nРешение:\n1. Дано: $a = 5$, $b = 3$\n2. Найти: $a + b$\n3. Решение: $5 + 3 = 8$\n\nОтвет: 8')
    print('Created: sample_answer.txt')

    print('\nSample assets created successfully!')
