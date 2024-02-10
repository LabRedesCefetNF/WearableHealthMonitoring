 Este trabalho apresenta o desenvolvimento e implementação de um protótipo \textit{wearable} de monitoramento de saúde concebido para idosos em instituições de cuidados. 
 O sistema proposto integra sensores não intrusivos e minimamente invasivos, incluindo frequência cardíaca (Amped 1.5), temperatura corporal (LM35) e acelerômetro (ADXL345), em um protótipo vestível integrado a uma camisa. 
 Os dados coletados por esses sensores são processados pelo Arduino Mega 2560 e transmitidas sem fio para um servidor remoto por meio do transmissor RF de 433 MHz (FS1000A). 
 O sistema foi projetado para oferecer monitoramento em tempo real para vários indivíduos simultaneamente, visando aumentar a eficiência no cuidado. 
 A configuração do hardware inclui ainda o uso de uma bateria recarregável (Power bank) para garantir autonomia ao dispositivo. 
 Os dados enviados pelo transmissor RF de 433 MHz (RWS-371-6) são recebidos por outro Arduino Mega 2560 conectado a uma Ethernet Shield para armazená-los temporariamente. 
 Com o intuito de automatizar a recuperação desses dados do servidor web, o armazenamento local e a visualização gráfica, desenvolvemos um script Python. 
 Este script foi implementado no dispositivo local do respectivo cuidador, proporcionando uma visão abrangente dos parâmetros de saúde do indivíduo monitorado. 
 A funcionalidade do sistema foi validada por meio de um estudo de caso que envolveu a prova de conceito do monitoramento de um indivíduo em diversos cenários, incluindo simulações de quedas, para verificar sua viabilidade e desempenho. 
 O protótipo proposto apresenta uma solução viável para monitoramento remoto da saúde, oferecendo aos cuidadores acesso seguro e eficiente a dados em tempo real, facilitando respostas oportunas a emergências. 
 Esta pesquisa contribui para o avanço dos sistemas vestíveis de monitoramento de saúde, atendendo à crescente necessidade de soluções confiáveis e discretas em instalações de atendimento a idosos.

 Palavras-Chave: Wearable; Monitoramento de Saúde; Idosos.

 Link do vídeo do protótipo: https://www.youtube.com/watch?v=Uvz3LJdC63M
