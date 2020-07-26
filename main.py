from github import Github
import sys
import re
import base64
import os

head = '''<table>
<tr>'''
tail = '''
</tr>
</table>'''

def github_login(ACCESS_TOKEN, REPO_NAME):
    '''
    Use Pygithub to login to the repository

    Args:
        ACCESS_TOKEN (string): github Access Token
        REPO_NAME (string): repository name

    Returns:
        github.Repository.Repository: object represents the repo

    References:
    ----------
    [1]https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository
    '''
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(REPO_NAME)
    return repo

def get_inputs(input_name):
    '''
    Get a Github actions input by name

    Args:
        input_name (str): input_name in workflow file

    Returns:
        string: action_input

    References
    ----------
    [1] https://help.github.com/en/actions/automating-your-workflow-with-github-actions/metadata-syntax-for-github-actions#example
    '''
    return os.getenv('INPUT_{}'.format(input_name).upper())

def generate_contributors(repo, COLUMN_PER_ROW, img_width, font_size, head_format, tail_format):
    '''
    Generate the contributors list using a given template

    Args:
        repo (github.Repository.Repository): object represents the repo
        COLUMN_PER_ROW (int): number of contributors per row
        img_width (int): width of img
        font_size (int): font size of name
        head_format (string): html_format for table head
        tail_format (string): html_format for table tail

    Returns:
        string: contributors list
    '''    
    USER = 0
    HEAD = head_format
    TAIL = tail_format
    contributors = repo.get_contributors()
    for contributor in contributors:
        name = contributor.name
        avatar_url = contributor.avatar_url
        html_url = contributor.html_url
        if re.match('https://github.com/apps/', html_url):
            continue
        if name == None:
            name = html_url[19:]
        if USER >= COLUMN_PER_ROW:
            new_tr = '''\n</tr>\n<tr>'''
            HEAD = HEAD + new_tr
            USER = 0
        td = f'''
    <td align="center">
        <a href={html_url}>
            <img src={avatar_url} width="{img_width};" alt={name}/>
            <br />
            <sub style="font-size:{font_size}px"><b>{name}</b></sub>
        </a>
    </td>'''
        HEAD = HEAD + td
        USER += 1
    HEAD = HEAD + TAIL
    return HEAD


def write_contributors(repo, contributors_list, path, commit_message, CONTRIB):
    '''
    Write contributors list to file if it differs

    Args:
        repo (github.Repository.Repository): object represents the repo
        contributors_list (string): contributors list
        path (string): the file to write
        commit_message (string): commit message
        CONTRIB (string): where you want to write the contributors list
    '''
    contents = repo.get_contents(path)
    base = contents.content
    base = base.replace('\n', '')
    text = base64.b64decode(base).decode('utf-8')
    str = text.split(CONTRIB)
    if re.match(head, str[1]):
        end = str[1].split(tail)
        end[0] = end[0] + tail
    else:
        end = ['', str[1]]
    if end[0] != contributors_list:
        end[0] = contributors_list
        text = str[0] + CONTRIB + end[0] + end[1]
        repo.update_file(contents.path, commit_message, text, contents.sha)
    else:
        pass

def main():
    ACCESS_TOKEN = get_inputs('ACCESS_TOKEN')
    REPO_NAME = get_inputs('REPO_NAME')
    CONTRIB = get_inputs('CONTRIB') + '\n\n'
    COLUMN_PER_ROW = int(get_inputs('COLUMN_PER_ROW'))
    IMG_WIDTH = int(get_inputs('IMG_WIDTH'))
    FONT_SIZE = int(get_inputs('FONT_SIZE'))
    PATH = get_inputs('PATH')
    COMMIT_MESSAGE = get_inputs('COMMIT_MESSAGE')
    repo = github_login(ACCESS_TOKEN, REPO_NAME)
    CONTRIBUTORS_LIST = generate_contributors(repo, COLUMN_PER_ROW, IMG_WIDTH, FONT_SIZE, head, tail)
    write_contributors(repo, CONTRIBUTORS_LIST, PATH, COMMIT_MESSAGE, CONTRIB)


if __name__ == '__main__':
    main()