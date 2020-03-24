import matplotlib.pyplot as plt
import numpy as np
import sys
import concurrent.futures


def Main():
    Time = np.arange(0, 0.10001, 0.00001) # 分解能:10uSec
    SinFreq = 20 # 変調波周波数
    TriFreq = 60 # 搬送波周波数（キャリア周波数）
    TriN = 20 # 三角波項数

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        SinU_future = executor.submit(MakeSin, Time, SinFreq, 0) # U相サイン波生成
        SinV_future = executor.submit(MakeSin, Time, SinFreq, 120) # V相サイン波生成
        SinW_future = executor.submit(MakeSin, Time, SinFreq, 240) # W相サイン波生成
        TriWave_future = executor.submit(Tri, Time, TriFreq, TriN) # 三角波生成
    SinU = SinU_future.result()
    SinV = SinV_future.result()
    SinW = SinW_future.result()
    TriWave = TriWave_future.result()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        PwmU_future = executor.submit(Pwm, SinU, TriWave, Time) # U相PWM波生成
        PwmV_future = executor.submit(Pwm, SinV, TriWave, Time) # V相PWM波生成
        PwmW_future = executor.submit(Pwm, SinW, TriWave, Time) # W相PWM波生成
    PwmU = PwmU_future.result()
    PwmV = PwmV_future.result()
    PwmW = PwmW_future.result()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        VvvfU_future = executor.submit(VVVF, PwmU, PwmV, Time) # U相-V相間VVVF波形
        VvvfV_future = executor.submit(VVVF, PwmV, PwmW, Time) # V相-W相間VVVF波形
        VvvfW_future = executor.submit(VVVF, PwmW, PwmU, Time) # W相-U相間VVVF波形
    VvvfU = VvvfU_future.result()
    VvvfV = VvvfV_future.result()
    VvvfW = VvvfW_future.result()

    # U相グラフ描画
    plt.subplot(3, 2, 1)
    plt.title("U Phase", fontsize=15)
    plt.plot(Time, SinU, label="Sin")
    plt.plot(Time, TriWave, label="Tri")
    plt.plot(Time, PwmU, label="PWM")
    plt.legend(loc="lower right", fontsize=10)
    plt.subplot(3, 2, 2)
    plt.title("U-V", fontsize=15)
    plt.plot(Time, VvvfU)
    # V相グラフ描画
    plt.subplot(3, 2, 3)
    plt.title("V Phase", fontsize=15)
    plt.plot(Time, SinV, label="Sin")
    plt.plot(Time, TriWave, label="Tri")
    plt.plot(Time, PwmV, label="PWM")
    plt.legend(loc="lower right", fontsize=10)
    plt.subplot(3, 2, 4)
    plt.title("V-W", fontsize=15)
    plt.plot(Time, VvvfV)
    # W相グラフ描画
    plt.subplot(3, 2, 5)
    plt.title("W Phase", fontsize=15)
    plt.plot(Time, SinW, label="Sin")
    plt.plot(Time, TriWave, label="Tri")
    plt.plot(Time, PwmW, label="PWM")
    plt.legend(loc="lower right", fontsize=10)
    plt.subplot(3, 2, 6)
    plt.title("W-U", fontsize=15)
    plt.plot(Time, VvvfW)

    plt.figtext(0, 0, "Tri: {}Hz, Sin: {}Hz, VVVF: {}Hz".format(TriFreq, SinFreq, SinFreq))
    plt.show()


def MakeSin(t, f, p): #サイン波生成関数（ラッパー）
    # t: 時間（配列）
    # f: 周波数
    # p: 位相(Deg)
    wave = [] # 波形
    for i in t:
        wave.append(Sin(i, f, p))
    return wave


def Sin(t, f, p): #サイン波生成関数
    # t: 時間（配列）
    # f: 周波数
    # p: 位相(Deg)
    return np.sin(2 * np.pi * f * t + (p / 180 * np.pi))

def Tri(t, f, n): # 三角波生成関数
    # t: 時間（配列）
    # f: 周波数
    # n: 項数（整数）
    p = 0 # 合成波の元
    c = 1 # カウンタ
    for i in np.arange(1, 2 * n - 1, 2):
        if c % 2 == 0:
            p += (1/i**2) * Sin(t, f * i, 0)
        else:
            p -= (1/i**2) * Sin(t, f * i, 0)
        c += 1
    return 8/(np.pi**2)*p

def Pwm(w1, w2, t): # PWM波生成関数
    # w1: 波形1（配列）
    # w2: 波形2（配列）
    # t: 時間（配列）
    wave = [] # 波形
    for i in range(0, len(t)):
        if w1[i] > w2[i]:
            wave.append(1)
        else:
            wave.append(0)
    return wave

def VVVF(w1, w2, t): # VVVF波形生成関数
    # w1: 波形1（配列）
    # w2: 波形2（配列）
    # t: 時間（配列）
    wave = [] # 波形
    for i in range(0, len(t)):
        wave.append(w1[i] - w2[i])
    return wave

if __name__ == "__main__":
    Main()
    sys.exit(0)