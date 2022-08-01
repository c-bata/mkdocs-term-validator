import re
import logging

from mkdocs.config import config_options
import mkdocs.plugins

logger = logging.getLogger(__name__)
NG_WORDS = []

# compiled re objects
find_parethesis = re.compile(r'\(([^)]*)\)').findall
find_question_exclamation = re.compile(r'([ぁ-んァ-ヶー一-龠]+)([!?]+)').findall
sub_dot_space = re.compile(r'([^\d,.])\. ').sub
sub_dot_newline = re.compile(r'([^\d,.])\.\n').sub
sub_dot_eol = re.compile(r'([^\d,.])\.$').sub
sub_comma_space = re.compile(r'([^,.]), ').sub
sub_comma_newline = re.compile(r'([^,.]),\n').sub
sub_comma_eol = re.compile(r'([^,.]),$').sub
find_numofunit = re.compile(r'([^\w.%=()+-])(\d+)([A-Za-z]+)[^\d]').findall


class TermValidatorPlugin(mkdocs.plugins.BasePlugin):
    config_scheme = (
        ('rule_dic_file', config_options.Type(str, default=None)),
        ('console_output_only', config_options.Type(bool, default=False)),
    )

    def on_pre_build(self, config):
        if self.config['rule_dic_file']:
            load_ng_word_dic(self.config['rule_dic_file'])

    def on_page_markdown(self, markdown, page, config, files):
        new_lines = []
        for lineno, line in enumerate(markdown.split("\n")):
            new_lines.append(line)

            for finder, ng, good in NG_WORDS:
                found = finder(line)
                if not found:
                    continue
                msg = f"{page.file.src_path}:{lineno} Detect NG word: {found.group(0)} -> {good}"
                logger.warning(msg)
                if not self.config['console_output_only']:
                    new_lines.extend([
                        "!!! warning",
                        "    " + msg,
                        ""
                    ])

        return "\n".join(new_lines)


def load_ng_word_dic(ng_word_rule_file: str) -> None:
    """
    NGワードの辞書ファイルへのパスを指定します。
    辞書ファイルはUTF-8エンコーディングで、以下の形式で記載します::
        正規表現<tab文字>指摘内容
    空行と、行頭が#の行はスキップします
    :param str ng_word_rule_file:
        * None: use default rule file (default)
        * filepath: path to NG word dic file
    """
    global NG_WORDS
    with open(ng_word_rule_file, 'r', encoding='utf-8') as f:
        lines = (
            line.split('\t', 1)
            for line in f
            if line and (not line.startswith('#')) and ('\t' in line)
        )
        NG_WORDS = [
            (re.compile('(%s)' % ng.strip()).search, ng.strip(), good.strip())
            for ng, good in lines
        ]
