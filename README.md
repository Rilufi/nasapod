# nasapod
Bot em Python para postar informações sobre o Astronomy Picture of the Day da NASA

## Instalações
Único pacote externo necessário é o da nasa, já que urllib já vem normalmente por padrão:
$ pip install nasa

## NASA API
é necessário pedir uma key para o API da NASA, pra isso é só entrar no site e preencher seu nome e email em "Generate API Keys" https://api.nasa.gov/ não esqueça de incluir essas keys no credential.py em nasa_key

## O que o bot faz?
Bot consiste em pegar imagem + texto do APOD, assim como a referência do site. Para o texto ele corta em tweets de no máximo 280 caracteres, cortando até a última palavra, para não acontecer de cortar palavras no meio. Todos os tweets após o primeiro contendo a imagem e referência são respostas seguidas, só é necessário fornecer o usuário trocando 'user' em toReply = "user"

## + infos
Como esse bot é irmão do meu outro bot pra dados do covid, qualquer outra informação sobre python, pip e API do Twitter podem ser encontradas em https://github.com/Rilufi/coronga

## e deu certo?
Opa, pra checar os resultados só procurar o [Nasobot](https://twitter.com/nasobot)
