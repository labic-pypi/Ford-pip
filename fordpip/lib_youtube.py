
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
import csv
import os
import json
from tqdm import tqdm
import unicodedata
import itertools

try:
    from pyyoutube import Api
except ImportError:
    print("Warning: You need to install pyyoutube to use youtube collector. Run: pip install pyyoutube")
    Api = None

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    print("Warning: You need to install youtube_transcript_api to download transcripts. Run: pip install youtube_transcript_api")
    YouTubeTranscriptApi = None

try:
    from pythumb import Thumbnail
except ImportError:
    print("Warning: You need to install pythumb to download thumbnails. Run: pip install pythumb")
    Thumbnail = None

try:
    from pytube import YouTube
except ImportError:
    print("Warning: You need to install pytube to download videos. Run: pip install pytube")
    YouTube = None

def checkYoutubeCredentials(fordPath):
    if path.exists(fordPath + '/lib/youtube/configs.json'):
        # return the API key from the configs.js file
        with open(fordPath + '/lib/youtube/configs.json') as f:
            data = f.read()
            data = json.loads(data)
            if "api_key" in data:
                return data["api_key"]
    print("You need a youtube API Key to use youtube collector")
    print("Create a API Key in https://console.developers.google.com/apis/")
    print("Open " + fordPath + "/lib/youtube/configs-example.json file")
    print("Replace <your-api-key-here> to your API key")
    print("Save as configs.json in same folder")
    print("then try again")
    return False

def parse_date(date):
    try:
        date = date.split("/")
        date = f"{date[2]}-{date[1]}-{date[0]}"
        return date
    except Exception:
        return None

def to_csv(title,header,data):
    file_path = title
    with open(file_path, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header) # write the header
        for d in data:
            writer.writerow(d) # write the data

def get_videos(api, q, count=None, start_date=None, end_date=None, region_code="BR", order="relevance"):
    if not api:
        key = checkYoutubeCredentials()
        if not key:
            exit()
        api = Api(api_key=os.getenv("YOUTUBE_API_KEY"))

    if start_date: start_date = f"{start_date}T00:00:00Z"
    if end_date: end_date = f"{end_date}T23:59:59Z"

    r = api.search(
        region_code=region_code,
        #location="21.5922529, -158.1147114",
        #location_radius="10mi",
        q=q,
        parts=["snippet"],
        count=count,
        published_after=start_date,
        published_before=end_date,
        safe_search=None, # none, "moderate", "strict"
        search_type="video",
        #return_json=True,
        order=order,
        relevance_language="pt",
        )
    return r

def get_video_details(api, video_ids):
    if not api:
        key = checkYoutubeCredentials()
        if not key:
            exit()
        api = Api(api_key=os.getenv("YOUTUBE_API_KEY"))

    response = []

    while len(video_ids) > 0:

        videos_ids_part = video_ids[:50]
        video_ids = video_ids[50:]

        r = api.get_video_by_id(
            video_id=','.join(videos_ids_part),
        )

        response.append(r)

    return response


def youtube_search(args):

    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return
    
    search = input("Digite o que deseja pesquisar: ")

    num = None
    while not num:
        try:
            num = int(input("Digite a quantidade de vídeos que deseja obter: "))
        except ValueError:
            print("Digite um número válido.")
            num = None

    start_date = None
    while not start_date:
        start_date = input("Vídeos publicados a partir de (dd/mm/aaaa): ")
        if start_date == "":
            start_date = None
            break
        start_date = parse_date(start_date)
        if not start_date:
            print("Digite uma data válida.")

    end_date = None
    while not end_date:
        end_date = input("Vídeos publicados até (dd/mm/aaaa): ")
        if end_date == "":
            end_date = None
            break
        end_date = parse_date(end_date)
        if not end_date:
            print("Digite uma data válida.")

    # date – Os recursos são classificados em ordem cronológica inversa, com base na data em que foram criados.
    # rating – Os recursos são classificados da maior para a menor classificação.
    # relevance – Os recursos são classificados com base na relevância para a consulta de pesquisa. Este é o valor padrão para este parâmetro.
    # title – Os recursos são classificados em ordem alfabética por título.
    # videoCount – Os canais são classificados em ordem decrescente do número de vídeos enviados.
    # viewCount – Os recursos são classificados do maior para o menor número de visualizações. Para transmissões ao vivo, os vídeos são classificados pelo número de espectadores simultâneos enquanto as transmissões estão em andamento.

    order ='relevance'
    print("Defina a ordem de listagem dos vídeos:")
    print("1 - Rating")
    print("2 - Relevance")
    print("3 - Title (Ordem alfabética)")
    print("4 - View Count")
    print("5 - Date (Ordem cronológica inversa)")
    input_order = input("Digite o número da opção desejada: ")

    if input_order == "1": order = "rating"
    elif input_order == "2": order = "relevance"
    elif input_order == "3": order = "title"
    elif input_order == "4": order = "viewCount"
    elif input_order == "5": order = "date"
    else: print("Opção inválida. A ordem padrão será utilizada.")

    api = Api(api_key = key)
    print("\nBuscando...")
    videos = get_videos(api, search, num, start_date, end_date, region_code="BR", order=order)

    print(f"\nExistem {videos.pageInfo.totalResults} resultados para essa busca.")
    print(f"Foram baixados os IDs de {len(videos.items)} vídeos.")
    print("Obtendo metadados...")

    ids = [ video.id.videoId for video in videos.items ]

    metadados = get_video_details(api, ids)

    metadados = [metadado.items for metadado in metadados]
    metadados = [item for sublist in metadados for item in sublist]

    print(f"Foram baixados os metadados de {len(metadados)} videos.")

    #countlike
    #videoduration
    #location
    #type

    header = ['id', 'title', 'description', 'countLike', 'viewCount', 'commentCount', 'duration', 'location', 'type',
              'publishedAt', 'channelId', 'channelTitle', 'liveBroadcastContent', 'text', 'tags']
    data = []

    for video in metadados:
        text = f"{video.snippet.title} {video.snippet.description}"
        tags = ','.join(video.snippet.tags) if video.snippet.tags else ''
        dados = [video.id, video.snippet.title, video.snippet.description, video.statistics.likeCount, video.statistics.viewCount,
                 video.statistics.commentCount, video.contentDetails.duration, '', video.snippet.liveBroadcastContent,
                 video.snippet.publishedAt, video.snippet.channelId, video.snippet.channelTitle, video.snippet.liveBroadcastContent, text, tags]
        data.append(dados)
    to_csv("videos.csv",header,data)

    print("\nArquivo salvo com sucesso.")
    return



def youtube_search_bychannel(args):
    
    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return
    
    channel_ids = []
    query = input('Please enter the channel_ids (separated by comma) or file (csv or txt) to search: ')
    # check if have a file
    if path.exists(query):
        with open(query, 'r') as file:
            if query.endswith('.csv'):
                csvreader = csv.DictReader(file)
                col = 'channelId'
                # check if column exists
                while col not in csvreader.fieldnames:
                    print(f"A coluna {col} não existe no arquivo.")
                    col = input("Digite o nome da coluna com os IDs dos canais: ")

                channel_ids = [row["id"] for row in csvreader]
            else:
                channel_ids = [line.strip() for line in file]
    else:
        channel_ids = query.split(',')

    print(f"{len(channel_ids)} IDs de canais encontrados.")

    return



def youtube_comments(args=None, video_ids=None):
    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return

    if not video_ids:
        video_ids = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os IDs dos vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv') and not filename.endswith('.txt'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            if filename.endswith('.csv'):
                csvreader = csv.DictReader(file)
                col = 'id'
                # check if column exists
                while col not in csvreader.fieldnames:
                    print(f"A coluna {col} não existe no arquivo.")
                    col = input("Digite o nome da coluna com os IDs dos vídeos: ")

                for row in csvreader:
                    video_ids.append(row["id"])
            else:
                for line in file:
                    video_ids.append(line.strip())

    print(f"{len(video_ids)} IDs de vídeos encontrados.")

    if not os.path.exists("./comments"):
        os.mkdir("./comments")

    api = Api(api_key = key)
    print("\nBaixando comentários...")

    for video_id in tqdm(video_ids):
        try:
            comments_by_video = api.get_comment_threads(video_id=video_id)
            header = ['id', 'author', 'text', 'publishedAt', 'likeCount']
            data = []
            for comment in comments_by_video.items:
                dados = [comment.id, comment.snippet.topLevelComment.snippet.authorDisplayName, comment.snippet.topLevelComment.snippet.textDisplay, comment.snippet.topLevelComment.snippet.publishedAt, comment.snippet.topLevelComment.snippet.likeCount]
                data.append(dados)
            to_csv(f"comments/{video_id}.csv",header,data)
        except Exception:
            print(f"Erro ao baixar comentários do vídeo {video_id}.")

    print("\nComentários baixados com sucesso.")
    return


            
def youtube_transcriptions(args=None, video_ids=None, languages=["pt-BR", "pt", "en"]):

    if not video_ids:
        video_ids = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os IDs dos vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv') and not filename.endswith('.txt'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            if filename.endswith('.csv'):
                csvreader = csv.DictReader(file)
                col = 'id'
                # check if column exists
                while col not in csvreader.fieldnames:
                    print(f"A coluna {col} não existe no arquivo.")
                    col = input("Digite o nome da coluna com os IDs dos vídeos: ")

                for row in csvreader:
                    video_ids.append(row["id"])
            else:
                for line in file:
                    video_ids.append(line.strip())

    print(f"{len(video_ids)} IDs de vídeos encontrados.")

    if not os.path.exists("./transcripts"):
        os.mkdir("./transcripts")

    erros = 0
    sucessos = 0

    print("\nBaixando transcricoes...")

    for video_id in tqdm(video_ids):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        except Exception:
            erros += 1
            continue
        # Salva legenda em arquivo csv
        header = ["start", "duration", "text"]
        data = []
        for t in transcript:
            dados = [t["start"], t["duration"], t["text"]]
            data.append(dados)
        to_csv(f"transcripts/{video_id}.csv",header,data)
        sucessos += 1
    
    print(f"\n{sucessos} transcricoes baixadas com sucesso.")
    print(f"{erros} vídeos sem transcricoes disponíveis.")
    return




def youtube_thumbnails(args=None, video_ids=None):

    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return

    if not video_ids:
        video_ids = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os IDs dos vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv') and not filename.endswith('.txt'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            if filename.endswith('.csv'):
                csvreader = csv.DictReader(file)
                col = 'id'
                # check if column exists
                while col not in csvreader.fieldnames:
                    print(f"A coluna {col} não existe no arquivo.")
                    col = input("Digite o nome da coluna com os IDs dos vídeos: ")

                for row in csvreader:
                    video_ids.append(row["id"])
            else:
                for line in file:
                    video_ids.append(line.strip())

    print(f"{len(video_ids)} IDs de vídeos encontrados.")

    if not os.path.exists("./thumbnails"):
        os.mkdir("./thumbnails")

    print("\nBaixando thumbnails...")
    for video_id in tqdm(video_ids):
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            t = Thumbnail(url)
            t.fetch()
            t.save(f"./thumbnails/")
        except Exception:
            print(f"Erro ao baixar thumbnail do vídeo {video_id}.")


def youtube_videos(args=None, video_ids=None):

    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return

    if not video_ids:
        video_ids = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os IDs dos vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv') and not filename.endswith('.txt'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            if filename.endswith('.csv'):
                csvreader = csv.DictReader(file)
                col = 'id'
                # check if column exists
                while col not in csvreader.fieldnames:
                    print(f"A coluna {col} não existe no arquivo.")
                    col = input("Digite o nome da coluna com os IDs dos vídeos: ")

                for row in csvreader:
                    video_ids.append(row["id"])
            else:
                for line in file:
                    video_ids.append(line.strip())

    print(f"{len(video_ids)} IDs de vídeos encontrados.")

    if not os.path.exists("./videos"):
        os.mkdir("./videos")

    print("\nBaixando vídeos...")
    for video_id in tqdm(video_ids):
        try:
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(output_path="./videos", filename=video_id)
        except Exception:
            print(f"Erro ao baixar vídeo {video_id}.")




def youtube_parse(args=None):
    print("Please enter the action to take: ")
    print("1 - Tags Graph")
    print("2 - Tag-Channel Graph")

    choice = None

    while not choice:
        choice = input("> ")
        if choice not in ["1", "2"]:
            print("Invalid choice.")
            choice = None
    if choice == "1":
        youtube_tags_graph(args)
    elif choice == "2":
        youtube_tag_channel_graph(args)
    return

def youtube_tags_graph(args=None, videos=None):

    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return

    if not videos:
        videos = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            csvreader = csv.DictReader(file)
            col = 'description'
            # check if column exists
            while col not in csvreader.fieldnames:
                print(f"A coluna {col} não existe no arquivo.")
                col = input("Digite o nome da coluna com as descricoes dos vídeos: ")

            for row in csvreader:
                videos.append(row["description"])

    print(f"{len(videos)} vídeos encontrados.")

    tags_pairs = []
    for video in videos:
        tags = []
        for word in video.split():
            if word.startswith("#"):
                # remove accents
                word = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('ASCII')
                # remove cedilha
                word = word.replace("ç", "c").lower()
                tags.append(word)
        for pair in itertools.combinations(tags, 2):
            tags_pairs.append(pair)

    nodes = set()
    edges = []

    for pair in tags_pairs:
        nodes.add(pair[0])
        nodes.add(pair[1])
        edges.append(pair)

    # calculate weights (number of occurrences)
    weights = {}
    for edge in edges:
        if edge in weights:
            weights[edge] += 1
        elif (edge[1], edge[0]) in weights:
            weights[(edge[1], edge[0])] += 1
        else:
            weights[edge] = 1

    # Open a file
    with open('tags_graph.gdf', 'w') as f:
        # write nodes
        f.write("nodedef>name VARCHAR,label VARCHAR\n")
        for node in nodes:
            f.write(f"{node},{node}\n")
        # write edges
        f.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE\n")
        for key,value in weights.items():
            f.write(f"{key[0]},{key[1]},{value}\n")

    print("Graph saved as tags_graph.gdf.")
    return
        


def youtube_tag_channel_graph(args=None, videos=None):

    key = checkYoutubeCredentials(args['path_script'])
    if (not key):
        return

    if not videos:
        videos = []

        filename = 'videos.csv'
        if not os.path.exists(filename): filename = None

        while not filename:
            filename = input("Digite o nome do arquivo csv com os vídeos: ")
            # check if file exists
            if not os.path.exists(filename):
                print("Digite um nome de arquivo válido.")
                filename = None
                continue
            # check if file is a csv or txt file
            if not filename.endswith('.csv'):
                print("Digite um arquivo csv ou txt.")
                filename = None
                continue

        # read file
        with open(filename, 'r') as file:
            csvreader = csv.DictReader(file)
            col = 'description'
            # check if column exists
            while col not in csvreader.fieldnames:
                print(f"A coluna {col} não existe no arquivo.")
                col = input("Digite o nome da coluna com as descricoes dos vídeos: ")

            for row in csvreader:
                videos.append([row['channelId'], row['channelTitle'],row["description"]])

    print(f"{len(videos)} vídeos encontrados.")

    tag_channel_pairs = []
    channels = {}

    for channelid, channeltitle, desc in videos:
        channels[channelid] = channeltitle
        tags = []
        for word in desc.split():
            if word.startswith("#"):
                # remove accents
                word = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('ASCII')
                # remove cedilha
                word = word.replace("ç", "c").lower()
                tags.append(word)
        for tag in tags:
            tag_channel_pairs.append((tag, channelid))

    nodes = set()
    edges = []

    for pair in tag_channel_pairs:
        nodes.add((pair[0], pair[0], 'tag'))
        edges.append(pair)

    for channel in channels:
        nodes.add((channel, channels[channel], 'channel'))

    # calculate weights (number of occurrences)
    weights = {}
    for edge in edges:
        if edge in weights:
            weights[edge] += 1
        else:
            weights[edge] = 1

    nodes = list(nodes)

    # Open a file
    with open('tag_channel_graph.gdf', 'w') as f:
        # write nodes
        f.write("nodedef>name VARCHAR,label VARCHAR,type VARCHAR \n")
        for node in nodes:
            f.write(f"{node[0]},'{node[1]}',{node[2]}\n")
        # write edges
        f.write("edgedef>node1 VARCHAR,node2 VARCHAR,weight DOUBLE\n")
        for key,value in weights.items():
            f.write(f"{key[0]},{key[1]},{value}\n")

    print("Graph saved as tag_channel_graph.gdf.")
    return