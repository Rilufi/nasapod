# nasapod

Python bot to post the Astronomy Picture of the Day on Twitter/X and Instagram using the NASA API. It also posts the photo of the previous day from NASA's Instagram account on Twitter, and optionally processes videos.

## Installations
All required packages are listed in `requirements.txt`. You can install them using:

```
$ pip install -r requirements.txt
```

## NASA API
You need to request a key for the NASA API by visiting the website and filling in your name and email under "Generate API Keys" at [NASA API](https://api.nasa.gov/). Don't forget to include this key in `auth.py` under `nasa_key`.

## Google Generative AI
To use the Google Generative AI for translations, you need an API key. Configure the API key in your environment variables as `GOOGLE_API_KEY`.

## Twitter/X API
To post on Twitter/X, set up the Twitter API keys and tokens in `auth.py`. Ensure you have the necessary permissions to post media and text.

## Instagram API
To post on Instagram, use the `instagrapi` package. Make sure to provide your Instagram credentials in the environment variables.

## Threads API
To post on Threads, provide your Threads credentials in the environment variables.

## What does the bot do?
- **Posts the Astronomy Picture of the Day**: Retrieves the APOD from the NASA API and posts it on Twitter/X and Instagram.
- **Posts NASA's Instagram photo of the previous day on Twitter**: Downloads the latest photo from NASA's Instagram and posts it on Twitter with the original caption.
- **Handles different media types**: Supports posting images and videos, including video processing for Twitter's duration limits.

## Usage
The bot can be run with the main script which handles the entire process of fetching data, processing it, and posting it to social media platforms.

## Additional Information
For additional information about Python, pip, and the Twitter API, refer to my other project: [GitHub - Coronga](https://github.com/Rilufi/coronga).

## Check the results
To see the bot in action, check out [Nasobot on Twitter](https://twitter.com/nasobot) and [Apodinsta on Instagram](https://www.instagram.com/apodinsta/).

---

# nasapod

Bot em Python para postar a Astronomy Picture of the Day no Twitter/X e no Instagram usando a API da NASA. Também posta a foto do dia anterior da conta do Instagram da NASA no Twitter, e opcionalmente processa vídeos.

## Instalações
Todos os pacotes necessários estão listados em `requirements.txt`. Você pode instalá-los usando:

```
$ pip install -r requirements.txt
```


## NASA API
É necessário solicitar uma chave para a API da NASA visitando o site e preenchendo seu nome e e-mail em "Generate API Keys" em [NASA API](https://api.nasa.gov/). Não se esqueça de incluir essa chave em `auth.py` sob `nasa_key`.

## Google Generative AI
Para usar a Google Generative AI para traduções, você precisa de uma chave de API. Configure a chave da API nas variáveis de ambiente como `GOOGLE_API_KEY`.

## Twitter/X API
Para postar no Twitter/X, configure as chaves e tokens da API do Twitter em `auth.py`. Certifique-se de ter as permissões necessárias para postar mídia e texto.

## Instagram API
Para postar no Instagram, use o pacote `instagrapi`. Certifique-se de fornecer suas credenciais do Instagram nas variáveis de ambiente.

## Threads API
Para postar no Threads, forneça suas credenciais do Threads nas variáveis de ambiente.

## O que o bot faz?
- **Posta a Astronomy Picture of the Day**: Recupera a APOD da API da NASA e posta no Twitter/X e Instagram.
- **Posta a foto do dia anterior do Instagram da NASA no Twitter**: Baixa a foto mais recente do Instagram da NASA e posta no Twitter com a legenda original.
- **Manipula diferentes tipos de mídia**: Suporta a postagem de imagens e vídeos, incluindo o processamento de vídeos para limites de duração do Twitter.

## Uso
O bot pode ser executado com o script principal que lida com todo o processo de buscar dados, processá-los e postá-los nas plataformas de mídia social.

## Informações Adicionais
Para informações adicionais sobre Python, pip e a API do Twitter, consulte meu outro projeto: [GitHub - Coronga](https://github.com/Rilufi/coronga).

## Verificar os resultados
Para ver o bot em ação, confira [Nasobot no Twitter](https://twitter.com/nasobot) e [Apodinsta no Instagram](https://www.instagram.com/apodinsta/).
