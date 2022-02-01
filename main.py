import requests as re
import math
import argparse, sys

api = "https://harbor01.viavarejo.com.br/api/v2.0/"
api_harbor2 = "https://harbor02.viavarejo.com.br/api/v2.0/"
csrf_token = #Grab token from a request to the HARBOR API in the Header


def count_repos_by_project(project_name):
    repo_count = re.get(f'{api}projects/{project_name}').json()['repo_count']
    pages = math.ceil(repo_count / 100)
    return pages


def list_repos(project_name, dest_proj):
    # Configurar token acesso para repos privados
    pages = count_repos_by_project(project_name)

    for page in range(1, pages + 1):
        endpoint = f'projects/{project_name}/repositories?page_size=100&page={page}'
        response = re.get(f'{api}{endpoint}').json()

        for repo in response:
            repo = repo['name']
            repo = repo.split('/')[1:]
            repo = '%252F'.join(repo)

            # Chama metodo de copy
            copy_artifacts(dest_proj=dest_proj, repo=repo, src_project=project_name)


def list_artifacts(src_proj, repo):
    endpoint = f'projects/{src_proj}/repositories/{repo}/artifacts'

    response = re.get(url=f'{api}{endpoint}')

    data = response.json()
    digest = list()

    if response.status_code == 200:
        for artifact in data:
            digest.append(artifact['digest'])
    else:
        print(f'Describe -> {data} | {response.status_code}')

    return digest


def copy_artifacts(repo, dest_proj, src_project):
    digests = list_artifacts(src_project, repo)

    headers = {'Authorization': 'Basic MjEwNTA5MzM4NDpQN1NIYkJRP3BlcUFlYSFI', 'X-Harbor-Csrf-Token': csrf_token}

    for digest in digests:
        from_param = f'{src_project}/{repo.replace("%252F", "/")}@{digest}'
        endpoint = f'projects/{dest_proj}/repositories/{repo}/artifacts?from={from_param}'

        response = re.post(url=f'{api}{endpoint}', headers=headers)

        if response.status_code == 201:
            print(f'{from_param} copiado com sucesso.')
        else:
            print(f'Error -> Status code: {response.status_code}')
            print(f'Describe -> {response.text}')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--source", "-s", help="Passe o nome do projeto de origem.")
    parser.add_argument("--destination", "-d", help="Passe o nome do projeto de destino.")
    parser.add_argument("--erase", "-e", help="Apaga os artifacts antigos.")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    if len(args.source) < 1 and len(args.destination) < 1:
        print(f'Argumentos inválidos. Execute novamente!')
        parser.print_help()
        sys.exit(1)
    else:
        list_repos(project_name=args.source, dest_proj=args.destination)
