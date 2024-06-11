#!/bin/bash

# Criar o nome do experimento com base no dia e horário
nome_experimento=$(date +"%Y-%m-%d_%H-%M-%S")
dia=$(date +"%Y-%m-%d")
hora=$(date +"%H-%M-%S")

# Cria pasta do experimento
mkdir experimentos/$nome_experimento

# Copiar o conteúdo da pasta .template para a pasta do experimento
cp -R .template/* experimentos/$nome_experimento

# Definir nome do experimento, dia e horário
sed -i "s/@EXPERIMENT_ID@/${nome_experimento}/g" experimentos/$nome_experimento/technical_report.md
sed -i "s/@CURRENT_DAY@/${dia}/g" experimentos/$nome_experimento/technical_report.md
sed -i "s/@CURRENT_HOUR@/${hora}/g" experimentos/$nome_experimento/technical_report.md

echo "Experimento criado com sucesso em experimentos/${nome_experimento}"
