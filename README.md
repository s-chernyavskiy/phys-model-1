Моделирование №1: "Динамик"
=

Физические формулы, используемые для расчёта
-

- Движение сигнала, который в последствие преобразуется в звуковую волну выражается по законом:

    $f(t) = A \cdot \sin(2\pi\nu t)$, где:
    - $A = \frac{U}{20}$ - амплитуда сигнала *(1)*
    - $\nu$ - частота сигнала
- Положение катушки в текущий момент времени выражается законом:
  
    $y(t) = y_0 + A \cdot \sin(2\pi\nu t k)$, где
    - $y_0 = 0.015$ м - начальное положение катушки _[зависит от размера магнита (в данном случае 0.03 м)]_
    - $k$ - коэффициент ускорения движения катушки *(2)*
- Положение диффузора в текущий момент времени выражается законом:

    $y(t) = y_0 + A \cdot \sin(2\pi\nu t k)$
- Положение звуковой волны (график) выражается законом:
    
    $y(t) = \frac{U}{5} \cdot \sin(2\pi\nu(t_g - 0.1t))$, где
    - $t_g \in [0, 0.02]$ с - ось графика
- Положение фазы звуковой волны выражается законом:

    $\phi(t) = (\phi_0 + N) \mod \nu_s$, где
  - $\phi_0$ - начальная фаза
  - $N$ - количество кадров
  - $\nu_s$ - частота дискретизации _(44100 Гц)_

*(1):* ***при расчете производится деление на 20 из следующих соображений:***
```python
# audio/AudioHandler.audio_callback()

# ...
amplitude = self.current_voltage / 20.0
out_data[:, 0] = amplitude * np.sin(2 * np.pi * self.current_freq * t)
# ...
```

Библиотека для вывода звука [sounddevice](https://python-sounddevice.readthedocs.io/en/0.5.1/) на вход получает значения в диапазоне _[-1.0, 1.0]_.

При этом, программно можно выбрать значение входного напряжения в диапазоне _[0.1, 20.0]_ В.

Выходит, что когда программно выбираем значение больше _1 В_, звуковая карта начинает ["клиповать" звук](https://en.wikipedia.org/wiki/Clipping_(audio)).

Чтобы избежать этого, производим деление на 20.

*(2):* ***существование данного коэффициента абсолютно искусственно:***

1) Обновление кадров происходит с частотой 200 мс ([source](https://matplotlib.org/stable/api/_as_gen/matplotlib.animation.FuncAnimation.html), раздел `interval`).

    Если оставить его как есть, картинка будет обновляться очень редко, и заметить колебания будет еще трудно. 
~~Методом тыка~~ Опытным путем было установлено, что значение близкие к нулю (а точнее даже меньше 50), 
сильно влияют на производительность, отчего и было выбрано значение, равное 50.

2) Для частоты, например, 1000 Гц, период равен $T = \frac{1}{\nu} = 1 \cdot 10^{-3}$ с $= 1$ мс.

    Тоесть, за один кадр анимации приходится 50 колебаний, ровно как и в наш интервал, поэтому увидеть эти колебания невозможно.

**Было принято следующее решение**:

Объявим коэффициент k, который будет отражать скорость колебания волны. В нашем случае он равен следующему:
  
  $k = 1 <=> \nu \le 100$ Гц

  $k = \frac{\nu}{100} <=> \nu \ge 100$ Гц

Такой коэффициент существует исключительно в рамках этой работы, и его спокойно можно отключить, для того,
чтобы увидеть визуализацию более приближенную к реальному физическому процессу.

Для включения/выключения данного функционала, нужно раскомментировать этот участок кода:

```python
# ui/UiHandler._update()

# ...
speed_factor = max(1.0, self.freq_slider.val / 1) # / 100) [Раскомментировать для коэффициента k]
# ...
```

Запуск
-
1) Установить библиотеки в `requirements.txt`
2) Запустить `main.py`:
    ```bash
    python3 src/main.py
    ```
3) Наслаждаться визуализацией!

Вывод
-
Нами была создана упрощенная модель динамика _(вообще, строго говоря, скорее электродинамического громкоговорителя)_.
Мы усвоили, что динамик устроен таким образом:
1) Переменный электрический ток поступает на звуковую катушку
2) Ток взаимодействует с магнитным полем, которое генерируется от постоянного магнита
3) Звуковая катушка движется
4) Так как звуковая катушка соединена с диффузором:
   1) Когда катушка двигается вперед, диффузор сжимает область в динамике,
   2) Когда катушка двигается назад, диффузор разжимает область в динамике.
5) Колебания создают продольные волны
6) Продольные волны дальше усиливаются, для увеличения громкости звука*

_* - но не в нашем эксперименте_