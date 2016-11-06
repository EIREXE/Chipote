import sys
import random



class Chip8:
    def __init__(self):
        self.fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        self.keys = {
            0x1: False, 0x2: False, 0x3: False, 0xC: False,
            0x4: False, 0x5: False, 0x6: False, 0xD: False,
            0x7: False, 0x8: False, 0x9: False, 0xE: False,
            0xA: False, 0x0: False, 0xB: False, 0xF: False,
        }

        self.opcode = bytearray(2);
        self.memory = bytearray(4096);
        self.V = [0x00]*16;
        self.I = 0x0000;
        self.pc = 0x0000;
        self.screen_w = 64;
        self.screen_h = 32;
        self.screen = [False]*(64*32);
        self.delay_timer = 0x00
        self.sound_timer = 0x00
        self.stack = [0x0000] * 16
        self.sp = 0x0000
        self.key = [bytearray(2)]*16
        self.draw_flag = False
        self.waiting_for_key_press = False
        self.waiting_for_key_press_reg = 0
    def load_game(self, game):
        for index, byte in enumerate(game):
            self.memory[512+index] = byte

    def press_key(self, key):
        self.keys[key] = True
        if self.waiting_for_key_press:
            self.V[self.waiting_for_key_press_reg] = key
            self.waiting_for_key_press = False
            self.pc += 2;

    def release_key(self, key):
        self.keys[key] = False
        print("depressed: " + str(hex(key)))

    def initialize_vm(self):
        self.pc = 0x200
        self.sp = 0
        self.I = 0
        for index, byte in enumerate(self.fontset):
            self.memory[index] = byte
    def emulate_clocks(self, delta):
        if self.delay_timer > 0:
            self.delay_timer -= 60*delta
            if self.delay_timer < 0:
                self.delay_timer = 0
        if self.sound_timer > 0:
            self.sound_timer -= 60 * delta
            if self.sound_timer < 0:
                self.sound_timer = 0
    def emulate_cycle(self):
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc+1]
        opcode_test = opcode & 0xF000
        if opcode_test == 0x0000:

            if opcode == 0x00EE:
                self.subroutine_return()
            elif opcode & 0x00F0:
                self.clear_screen()
        elif opcode_test == 0x1000:
            self.jump_to_adress(opcode & 0x0FFF)


        # Subroutine Jump 0x2NNN
        elif opcode_test == 0x2000:
            self.subroutine_jump(opcode & 0x0FFF)

        elif opcode_test == 0x3000:
            self.skip_if_reg_equals_value((opcode&0x0F00) >> 8, opcode&0x00FF)
        elif opcode_test == 0x4000:
            self.skip_if_reg_not_equal_to_value((opcode&0x0F00) >> 8, opcode&0x00FF)
        elif opcode_test == 0x5000:
            self.skip_if_reg_equal_to_reg((opcode&0x0F00) >> 8, (opcode&0x00F0) >> 4)
        elif opcode_test == 0x6000:
            #0x6000 set reg to
            self.set_register_to_value((opcode & 0x0F00) >> 8, opcode & 0x00FF)
        elif opcode_test == 0x7000:
            self.add_value_to_reg((opcode & 0x0F00) >> 8, opcode & 0x00FF)
        elif opcode_test == 0x8000:
            v_x = (opcode & 0x0F00) >> 8
            v_y = (opcode & 0x00F0) >> 4
            if (opcode & 0xF00F) == 0x8000:

                self.load_reg_to_reg(v_x, v_y)
            if (opcode & 0xF00F) == 0x8001:
                self.or_regs(v_x, v_y)
            if (opcode & 0xF00F) == 0x8002:
                self.and_regs(v_x, v_y)
            if (opcode & 0xF00F) == 0x8003:
                self.xor_regs(v_x, v_y)
            if (opcode & 0xF00F) == 0x8004:
                self.add_regs(v_x, v_y)
            if (opcode & 0xF00F) == 0x8005:
                self.substract_regs(v_x, v_y)
            if (opcode & 0xF00F) == 0x8006:
                self.shift_reg_right(v_x, v_y)
            if (opcode & 0xF00F) == 0x8007:
                self.substract_regs_n(v_x, v_y)
            if (opcode & 0xF00F) == 0x800E:
                self.shift_reg_left(v_x, v_y)
        elif opcode_test == 0x9000:
            v_x = (opcode & 0x0F00) >> 8
            v_y = (opcode & 0x00F0) >> 4
            self.skip_if_reg_not_equal_to_reg(v_x, v_y)
        elif opcode_test == 0xA000:
            self.set_I_to_value(opcode & 0x0FFF)
        elif opcode_test == 0xB000:
            self.jump_to_adress_plus_V0(opcode & 0x0FFF)
        # RNG
        elif opcode_test == 0xC000:
            reg = (opcode & 0x0F00) >> 8
            number = opcode & 0x00FF
            self.random_number(reg, number)
        elif opcode_test == 0xD000:
            x_V = (opcode & 0x0F00) >> 8
            y_V = (opcode & 0x00F0) >> 4
            height = (opcode & 0x000F)
            self.draw_sprite(x_V, y_V, height)
        elif opcode_test == 0xE000:
            if opcode & 0x00FF == 0x9E:
                reg = (opcode & 0x0F00) >> 8
                self.skip_if_key_is_pressed(reg)
            elif opcode & 0x00FF == 0xA1:
                reg = (opcode & 0x0F00) >> 8
                self.skip_if_key_is_not_pressed(reg)
        elif opcode_test == 0xF000:
            if opcode & 0x00FF == 0x0007:
                reg = (opcode & 0x0F00) >> 8
                self.load_dt_timer_to_reg(reg)
            elif opcode & 0x00FF == 0x000A:
                reg = (opcode & 0x0F00) >> 8
                self.wait_until_key_press_to_reg(reg)
            elif opcode & 0x00FF == 0x0015:
                reg = (opcode & 0x0F00) >> 8
                self.set_delay_timer_from_reg(reg)
            elif opcode & 0x00FF == 0x0018:
                reg = (opcode & 0x0F00) >> 8
                self.set_sound_timer_from_reg(reg)
            elif opcode & 0x00FF == 0x001E:
                reg = (opcode & 0x0F00) >> 8
                self.add_reg_to_I(reg)
            elif opcode & 0x00FF == 0x0029:
                dig = (opcode & 0x0F00) >> 8
                self.set_I_to_sprite_location_for_digit(dig)
            elif opcode & 0x00FF == 0x0033:
                reg = (opcode & 0x0F00) >> 8
                self.write_bcd_to_I_from_reg(reg)
            elif opcode & 0x00FF == 0x0055:
                val = (opcode & 0x0F00) >> 8
                self.store_registers_until_value(val)
            elif opcode & 0x00FF == 0x0065:
                val = (opcode & 0x0F00) >> 8
                self.read_registers_until_value(val)


        else:
            sys.exit()
            self.pc += 2
    ## OPCODES

    #0x00E0
    def clear_screen(self):
        self.screen = [False]*(64*32);
        self.draw_flag = True
        self.pc += 2;
    #0x00FD
    def exit_interpreter(self):
        sys.exit()

    #0x00FE
    def disable_extended_screen(self):
        self.screen_h = 32
        self.screen_h = 64
        self.pc += 2

    #0x00FF
    def enable_extended_screen(self):
        self.screen_h = 64
        self.screen_w = 128
        self.pc += 2


    #0x00EE
    def subroutine_return(self):
        self.sp-=1
        self.pc = self.stack[self.sp]
        self.pc+=2
    #0x1NNN
    def jump_to_adress(self, adress):
        self.pc = adress
    #0x2NNN
    def subroutine_jump(self, adress):
        self.stack[self.sp] = self.pc
        self.sp += 1
        self.pc = int(adress)
    # 0x3XNN
    def skip_if_reg_equals_value(self, reg, value):
        if self.V[reg] == value:
            self.pc+=4
        else:
            self.pc+=2

    # 0x4XNN
    def skip_if_reg_not_equal_to_value(self, reg, value):
        if not self.V[reg] == value:
            self.pc += 4
        else:
            self.pc += 2

    # 0x5xy0
    def skip_if_reg_equal_to_reg(self, v_x, v_y):
        if self.V[v_x] == self.V[v_y]:
            self.pc += 4
        else:
            self.pc += 2



    # 0x6XNN NN = Number to store
    # X = REG
    def set_register_to_value(self, register, value):
        self.V[register] = value
        self.pc += 2

    # 0x7XNN
    def add_value_to_reg(self, reg, value):
        self.V[reg] = (self.V[reg] + value) % 256
        self.pc += 2
    # 0x8xy0
    def load_reg_to_reg(self, v_x, v_y):
        self.V[v_x] = self.V[v_y]
        self.pc += 2

    # 0x8xy1
    def or_regs(self, v_x, v_y):
        self.V[v_x] = self.V[v_x] | self.V[v_y]
        self.pc += 2

    # 0x8xy2
    def and_regs(self, v_x, v_y):
        self.V[v_x] = self.V[v_x] & self.V[v_y]
        self.pc += 2

    # 0x8xy3
    def xor_regs(self, v_x, v_y):
        self.V[v_x] = self.V[v_x] ^ self.V[v_y]
        self.pc += 2

    # 0x8xy4 - ADD Vx, Vy
    def add_regs(self, v_x, v_y):
        result = self.V[v_x] + self.V[v_y]
        if result > 255:
            self.V[0xF] = 0x1
        self.V[v_x] = result % 256
        self.pc += 2
    # 0x8xy5
    def substract_regs(self, v_x, v_y):
        if self.V[v_x] > self.V[v_y]:
            self.V[0xF] = 1
        else:
            self.V[0xF] = 0
        self.V[v_x] = (self.V[v_x] - self.V[v_y]) % 256
        self.pc += 2

    # 0x8xy6
    def shift_reg_right(self, v_x, v_y):
        value_to_shift = self.V[v_y]
        self.V[0xF] = value_to_shift & 0xF
        self.V[v_x] = value_to_shift >> 1
        self.pc += 2
    # 0x8xy7
    def substract_regs_n(self, v_x, v_y):
        if self.V[v_y] > self.V[v_x]:
            self.V[0xF] = 0
        else:
            self.V[0xF] = 1
        self.V[v_x] = (self.V[v_y] - self.V[v_x]) % 256
        self.pc += 2
    # 0x8xyE
    def shift_reg_left(self, v_x, v_y):
        if self.V[v_x] > 0:
            self.V[0x0]
        else:
            self.V[0x1]
        self.V[v_x] = self.V[v_y] << 1
        self.pc += 2

    # 0x9xy0
    def skip_if_reg_not_equal_to_reg(self, v_x, v_y):
        if not self.V[v_x] == self.V[v_y]:
            self.pc += 4
        else:
            self.pc += 2
    # 0xANNN
    def set_I_to_value(self, value):
        self.I = value
        self.pc += 2
    # 0xBNNN
    def jump_to_adress_plus_V0(self, adress):
        self.pc = adress + self.V[0]
    #0xCXNN NN = NUMBER TO AND
    # X = REG
    def random_number(self, register, value):
        result = value & random.randrange(0,255,1)
        self.V[register] = int(result)
        self.pc += 2
    #0xDXYN
    def draw_sprite(self, v_x, v_y, height):
        width = 8

        self.V[0xF] = 0x0
        x = self.V[v_x]
        y = self.V[v_y]
        for y_line in range(height):
            pixel_line = self.memory[self.I+y_line]
            for x_line in range(8):
                if (pixel_line & (0x80 >> x_line)) != 0:
                    current_value = self.screen[(x+x_line)%self.screen_w + ((y+y_line)%self.screen_h)*self.screen_w]
                    if current_value == True:
                        self.V[0xF] = 0x1
                    print(((x+x_line)) + (((y+y_line))*self.screen_w))
                    self.screen[((x+x_line)%self.screen_w) + (((y+y_line)%self.screen_h)*64)] ^= 1

        self.draw_flag = True
        self.pc += 2

    # 0xEX9E
    def skip_if_key_is_pressed(self, reg):
        key = self.V[reg]
        if self.keys[key]:
            self.pc += 4
        else:
            self.pc +=2

    # 0xEXA1
    def skip_if_key_is_not_pressed(self, reg):
        key = self.V[reg]
        if not self.keys[key]:
            self.pc += 4
        else:
            self.pc +=2

    #0xFX07
    def load_dt_timer_to_reg(self, reg):
        self.V[reg] = self.delay_timer
        self.pc += 2
    #0xFX07
    def wait_until_key_press_to_reg(self, reg):
        self.waiting_for_key_press = True
        self.waiting_for_key_press_reg = reg
    #0xFX15
    def set_delay_timer_from_reg(self, reg):
        self.delay_timer = self.V[reg]
        self.pc +=2

    #0xFX18
    def set_sound_timer_from_reg(self, reg):
        print("timer")
        self.sound_timer = self.V[reg]
        self.pc +=2

    #0xFX1E
    def add_reg_to_I(self, reg):
        self.I = self.I + self.V[reg]
        self.pc +=2

    def set_I_to_sprite_location_for_digit(self, digit):
        self.I = (digit*5)-5
        self.pc += 2

    def write_bcd_to_I_from_reg(self, reg):
        self.memory[self.I] = int(self.V[reg] / 100);
        self.memory[self.I + 1] = int((self.V[reg] / 10) % 10);
        self.memory[self.I + 2] = int((self.V[(reg) >> 8] % 100) % 10);
        self.pc += 2

    def store_registers_until_value(self, value):
        for index in range(value+1):
            self.memory[self.I + index] = self.V[index]
        self.pc += 2

    def read_registers_until_value(self, value):
        for index in range(value+1):
            self.V[index] = self.memory[self.I+index]
        self.pc += 2

    # 0xFFXY DEBUG DRAW, NOT PART OF THE STANDARD AT ALL
    def debug_draw_pixel(self, x_V, y_V):
        x = self.V[x_V]
        y = self.V[y_V]
        position = x + y*self.screen_w
        self.screen[position] = True
        self.pc += 2
        self.draw_flag = True
