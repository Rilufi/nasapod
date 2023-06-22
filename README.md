# nasapod
Bot em Python para postar postar a Astronomy Picture of the Day e fotos dos Mars rovers pelo API da NASA. Também identifica onde a ISS se encontra com um mapa atualizado.

## Instalações
Todos os pacotes necessários se encontram em requirements.txt, você pode instalar através do pip utilizando
$ pip install -r requirements.txt

## NASA API
É necessário pedir uma key para o API da NASA, pra isso é só entrar no site e preencher seu nome e email em "Generate API Keys" https://api.nasa.gov/ não esqueça de incluir essa key no auth.py em nasa_key

## Nominatim API
Para as informações geográficas sobre a localização da ISS também é necessário uma key. Depois de criar uma conta, acesse https://www.openstreetmap.org/user/<seu_usuário>/oauth_clients/new e coloque a chave dentro de whereiss.py.

## O que o bot faz?
Bot consiste em pegar imagem do APOD, assim como a referência do site.

## ISS
Em whereiss.py encontra-se um código para localizar a Estação Espacial Internacional (ISS), identificar se ela se encontra sobre algum país no momento e fazer um gráfico do mapa mundial identificando sua localização.

## Space Store
Como a conta cresceu, agora sou afiliado à [Space Store](https://thespacestore.com/), inclui uma lista de produtos para postar junto dos retuites contendo meu link de afiliado. 

## + infos
Como esse bot é irmão do meu outro bot pra dados do covid, qualquer outra informação sobre python, pip e API do Twitter podem ser encontradas em https://github.com/Rilufi/coronga

## e deu certo?
Opa, pra checar os resultados só procurar o [Nasobot](https://twitter.com/nasobot)
