import pygame
import random
import json
from time import sleep

# 初始化Pygame
pygame.init()

# 游戏窗口设置
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w - 100, info.current_h - 100
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("单词配对游戏")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 字体设置
FONT = pygame.font.SysFont("simhei", 32)

# 单词库配置（可修改）
WORD_FILE = "words.json"


class WordCard:
    def __init__(self, text, pos, is_chinese):
        self.text = text
        self.pos = pos
        self.is_chinese = is_chinese
        self.rect = pygame.Rect(pos[0], pos[1], 200, 50)
        self.selected = False
        self.target_pos = None
        # self.matched = False

    def draw(self, surface):
        color = BLUE if self.selected else BLACK
        if self.target_pos:
            pygame.draw.line(surface, GREEN, self.rect.center, self.target_pos, 3)
        pygame.draw.rect(surface, color, self.rect, 2)
        text_surf = FONT.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def move_towards_target(self):
        if self.target_pos:
            dx = self.target_pos[0] - self.rect.centerx
            dy = self.target_pos[1] - self.rect.centery
            self.rect.centerx += dx * 0.1
            self.rect.centery += dy * 0.1
            if abs(dx) < 2 and abs(dy) < 2:
                self.rect.center = self.target_pos
            # self.matched = True
            return True
        return False


def show_victory_screen():
    # 定义两个按钮的区域
    replay_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
    exit_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 50)
    while True:
        WIN.fill(WHITE)
        # 绘制通关文字
        victory_text = FONT.render("恭喜通关 d=====(^▽^*)b", True, RED)
        vt_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        WIN.blit(victory_text, vt_rect)

        # 绘制“再玩一次”按钮
        pygame.draw.rect(WIN, BLUE, replay_button_rect)
        replay_text = FONT.render("再玩一次", True, WHITE)
        rt_rect = replay_text.get_rect(center=replay_button_rect.center)
        WIN.blit(replay_text, rt_rect)

        # 绘制“退出”按钮
        pygame.draw.rect(WIN, BLUE, exit_button_rect)
        exit_text = FONT.render("退出", True, WHITE)
        et_rect = exit_text.get_rect(center=exit_button_rect.center)
        WIN.blit(exit_text, et_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if replay_button_rect.collidepoint(pos):
                    return True
                elif exit_button_rect.collidepoint(pos):
                    return False
        sleep(0.1)


def load_words():
    try:
        with open(WORD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"apple": "苹果", "banana": "香蕉", "cat": "猫", "dog": "狗"}


def save_words(words):
    with open(WORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)


def main():
    while True:
        words = load_words()
        word_pairs = list(words.items())
        random.shuffle(word_pairs)

        english_words = []
        chinese_words = []

        # 创建英文单词卡
        for i, (en, cn) in enumerate(word_pairs):
            english_words.append(WordCard(en, (100, 100 + i * 70), False))

        # 创建中文解释卡（随机顺序）
        random.shuffle(word_pairs)
        for i, (en, cn) in enumerate(word_pairs):
            chinese_words.append(WordCard(cn, (500, 100 + i * 70), True))

        selected_en = None
        selected_cn = None
        running = True
        clock = pygame.time.Clock()
        matches = []

        while running:
            WIN.fill(WHITE)

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    # 检查点击英文单词
                    for word in english_words:
                        if word.rect.collidepoint(pos):
                            selected_en = word
                            word.selected = not word.selected
                    # 检查点击中文解释
                    for word in chinese_words:
                        if word.rect.collidepoint(pos):
                            selected_cn = word
                            word.selected = not word.selected

            # 检查匹配
            if selected_en and selected_cn:
                en_text = selected_en.text
                cn_text = selected_cn.text
                if words.get(en_text) == cn_text:
                    # 匹配成功，设置动画
                    # selected_en.target_pos = selected_cn.rect.center
                    # selected_cn.target_pos = selected_en.rect.center
                    mid_x = (selected_en.rect.centerx + selected_cn.rect.centerx) / 2
                    mid_y = (selected_en.rect.centery + selected_cn.rect.centery) / 2
                    selected_en.target_pos = (mid_x, mid_y)
                    selected_cn.target_pos = (mid_x, mid_y)
                    matches.extend([selected_en, selected_cn])
                    english_words.remove(selected_en)
                    chinese_words.remove(selected_cn)

                else:
                    # 匹配失败，取消选择
                    selected_en.selected = False
                    selected_cn.selected = False
                selected_en = None
                selected_cn = None

            # 更新动画
            remove_list = []
            for word in matches:
                if word.move_towards_target():
                    remove_list.append(word)
            for word in remove_list:
                word.draw(WIN)

                matches.remove(word)

            # matches = [word for word in matches if not word.matched]

            # 绘制所有元素

            for word in english_words + chinese_words + matches:
                word.draw(WIN)

            if not english_words and not chinese_words and not matches:
                running = False

            pygame.display.flip()
            clock.tick(60)
        if not english_words and not chinese_words and not matches:
            if not show_victory_screen():
                break
        else:
            break
    pygame.quit()


if __name__ == "__main__":
    main()
