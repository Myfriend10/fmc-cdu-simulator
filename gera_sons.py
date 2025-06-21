import wave
import struct
import math

def gerar_beep(filename, duration_ms=500, freq=440, volume=0.5, sample_rate=44100):
    n_samples = int(sample_rate * duration_ms / 1000)
    wav_file = wave.open(filename, 'w')
    wav_file.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))

    for i in range(n_samples):
        sample = volume * math.sin(2 * math.pi * freq * (i / sample_rate))
        # converter para int16
        val = int(sample * 32767.0)
        data = struct.pack('<h', val)
        wav_file.writeframesraw(data)

    wav_file.close()

# Gera sons simples
gerar_beep('alerta_combustivel.wav', freq=440)  # beep padrão A4
gerar_beep('alerta_chegada.wav', freq=660)     # beep mais agudo

print("Arquivos alerta_combustivel.wav e alerta_chegada.wav gerados.")
