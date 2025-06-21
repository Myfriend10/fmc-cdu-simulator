# Simulador Básico de FMC/CDU - Flight Management Computer

Este projeto é uma simulação simplificada de um FMC/CDU (Flight Management Computer / Control Display Unit) usado em aeronaves comerciais. Foi desenvolvido em Python com interface gráfica Tkinter, com integração de mapa via Matplotlib e alertas sonoros.

---

## Funcionalidades

- Inserção de waypoints com latitude, longitude e distância.
- Cálculo de tempo estimado, consumo de combustível e ETA.
- Visualização das fases do voo: subida, cruzeiro e descida.
- Mapa gráfico da rota com indicação da posição atual da aeronave.
- Integração com posição GPS real ou simulada.
- Alertas sonoros para consumo crítico de combustível e chegada ao destino.

---

## Requisitos

- Python 3.8 ou superior
- Bibliotecas:
  - tkinter (geralmente já vem com Python)
  - matplotlib
  - requests
  - playsound
  - threading (built-in)

Para instalar as bibliotecas externas use:

```bash
pip install matplotlib requests playsound
