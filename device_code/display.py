import framebuf
import ubinascii

black = 0
white = 1

class Box:
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Picture:
    def __init__(self, bufImage, w, h):
        print(bufImage)
        self.fbImage = framebuf.FrameBuffer(bufImage, w, h, framebuf.MONO_HLSB)
        self.w = w
        self.h = h
        
# serveur de display
def p64(base64string,w,h):
    ba = ubinascii.a2b_base64(base64string)
    print(type(ba))
    return Picture(bytearray(ba), w,h)

class DisplayServer:
    
    def __init__(self,epd, width,height):
        assert epd is not None
        self.epd = epd
        self.width = width
        self.height = height
        
        # use a frame buffer
        # 400 * 300 / 8 = 15000 - thats a lot of pixels

        self.buf = bytearray(self.width * self.height // 8)
        self.fb = framebuf.FrameBuffer(self.buf, self.width, self.height, framebuf.MONO_HLSB)

    def clear(self):
        self.fb.fill(white)
        
    def update(self):
        self.epd.display_frame(self.buf)
        
    def text(self,box,text, border=None, color=black):
        if border is not None:
            self.fb.rect(box.x, box.y, box.w, box.h, border)
            
        cols = box.w // 8
        # for each row
        j = 0
        x = box.x - 8
        for i in range(0, len(text)):
            x += 8
            c = text[i]
            if c == "\n" or x >= box.x + box.w:
                j += 8;
                x = box.x
                continue
            # dont overflow text outside the box
            if j >= box.h:
                break
            self.fb.text(text[i], x, box.y + j, color)

            
    def picture(self, picture, x, y):
        assert picture is not None
        self.fb.blit(picture.fbImage, x, y)
        
    def execute(self, code):
        exec(code, {"d": self, "p64":p64})
        
    def box(self, x, y, w, h):
        return Box(x, y, w, h)
        
