# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------
import os
import sys
import time

sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../../sunfouner-voice-assistant'))

project = 'SunFounder Fusion HAT+'
copyright = f'{time.localtime().tm_year}, SunFounder'
author = 'www.sunfounder.com'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx_rtd_theme',
    #'sphinx_toolbox.collapse',
    'sphinx.ext.autosummary',
    # 'sphinx.ext.imgmath',     # 启用图片渲染数学公式
    'sphinx.ext.mathjax',     # 启用MathJax渲染数学公式
    'sphinx.ext.autodoc',     # 自动从代码提取文档
    'sphinx.ext.napoleon',    # 解析Google/NumPy风格文档
    'sphinx.ext.viewcode',    # 显示代码链接
    # 'sphinx.ext.intersphinx', # 跨项目引用SunFounder voice assistant
]

html_theme_options = {
    'flyout_display': 'attached'
}
# latex_engine = 'xelatex'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# AutoDoc settings
autodoc_mock_imports = [
    "luma",
    "smbus2",
    "pyaudio",
    "RPi",
    "gpiozero",
    "spidev",
    "evdev",
]
autodoc_default_options = {
    'member-order': 'bysource',
    'members': True,          # 默认显示类/函数成员
    'classes': True,          # 默认只显示类（过滤函数，可选）
    'show-inheritance': True, # 默认显示继承关系
    'undoc-members': False,   # 不显示无 docstring 的成员（避免杂乱）
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# 交叉引用设置
# intersphinx_mapping = {
#     'sunfounder_voice_assistant': (
#         'https://sunfounder-voice-assistant.readthedocs.io/en/latest/',
#         None  # 如果知道 objects.inv 路径，可替换为 'https://.../objects.inv'
#     ),
# }

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

#### RTD+

html_js_files = [
    'https://ezblock.cc/readDocFile/custom.js',
    './lang.js', # new
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/ace.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/ext-language_tools.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/theme-chrome.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/mode-python.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/mode-sh.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/monokai.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/xterm.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/FitAddon.js',
    'https://ezblock.cc/readDocFile/readTheDoc/src/js/readTheDocIndex.js',
]
html_css_files = [
    'https://ezblock.cc/readDocFile/custom.css',
    'https://ezblock.cc/readDocFile/readTheDoc/src/css/index.css',
    'https://ezblock.cc/readDocFile/readTheDoc/src/css/xterm.css',
]




# Multi-language

language = 'en' # Before running make html, set the language.
# language = 'de' # Before running make html, set the language.
# language = 'ja' # Before running make html, set the language.
locale_dirs = ['locale/'] # .po files for other languages are placed in the locale/ folder.

gettext_compact = False # Support for generating the contents of the folders inside source/ into other languages.



# links

rst_epilog = """

.. |link_sf_facebook| raw:: html

    <a href="https://bit.ly/raphaelkit" target="_blank">here</a>

.. |link_german_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/robot-hat-v4/de/latest/" target="_blank">Deutsch Online-Kurs</a>

.. |link_jp_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/robot-hat-v4/ja/latest/" target="_blank">日本語オンライン教材</a>

.. |link_en_tutorials| raw:: html

    <a href="https://docs.sunfounder.com/projects/robot-hat-v4/en/latest/" target="_blank">English Online-tutorials</a>

"""

# Open on a new page

rst_epilog += """


.. |link_aliyun| raw:: html

    <a href="https://bailian.console.aliyun.com/?spm=5176.29597918.J_SEsSjsNv72yRuRFS2VknO.2.40a37b08ic1XHy&tab=model#/api-key" target="_blank">Bailian console</a>

.. |link_rpi_connect| raw:: html

    <a href="https://www.raspberrypi.com/documentation/services/connect.html" target="_blank">Raspberry Pi Connect</a>


.. |link_qwen_inter| raw:: html

    <a href="https://www.alibabacloud.com/help/en/model-studio/get-api-key" target="_blank">Get API Key</a>

.. |link_ollama_hub| raw:: html

    <a href="https://ollama.com/library" target="_blank">Ollama Hub</a>

.. |link_ollama| raw:: html

    <a href="https://ollama.com/download" target="_blank">Ollama Download Page</a>

.. |link_piper_voice| raw:: html

    <a href="https://github.com/rhasspy/piper/blob/master/VOICES.md" target="_blank">Piper Voices</a>
    
.. |link_grok_ai| raw:: html

    <a href="https://console.x.ai/team/f424aae2-94c8-4602-91bf-af8452fda9a2/models" target="_blank">xAI Cloud Console</a>
    
.. |link_deepseek| raw:: html

    <a href="https://platform.deepseek.com/sign_in" target="_blank">Deepseek Platform</a>

.. |link_doubao| raw:: html

    <a href="https://console.volcengine.com/auth/login" target="_blank">Volcengine</a>

.. |link_openai_platform| raw:: html

    <a href="https://platform.openai.com/settings/organization/api-keys" target="_blank">OpenAI Platform</a>

.. |link_gemini_model| raw:: html

    <a href="https://ai.google.dev/gemini-api/docs/models#model-variations" target="_blank">Gemini Models</a>

.. |link_google_ai| raw:: html

    <a href="https://aistudio.google.com/" target="_blank">Google AI Studio</a>

.. |link_voice_options| raw:: html

    <a href="https://platform.openai.com/docs/guides/text-to-speech/voice-options" target="_blank">Voice options</a>

"""

