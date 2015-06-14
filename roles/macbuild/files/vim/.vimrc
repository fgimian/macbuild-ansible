" Make vim more useful
set nocompatible

" Disable filetype for Vundle installation
filetype off

" Set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" Let Vundle manage Vundle
Plugin 'gmarik/Vundle.vim'

" Complete Vundle initialisation
" (all of your plugins must be added before this line)
call vundle#end()

" Enable syntax and file-type highlighting
syntax on
filetype on
filetype plugin on
filetype indent on

" Set color scheme to molokai
colorscheme molokai
let g:molokai_original = 1

" Show the filename in the window titlebar
set title

" Enable line numbers
set number

" Widen the line number gutter a little
set nuw=5

" Highlight current line
set cursorline

" Always show status line
set laststatus=2

" Override the line number background color to appear transparent
hi LineNr ctermbg=234

" Show the cursor position
set ruler

" Set the long-line marker
set colorcolumn=80

" Enable smart indent
set smartindent

" Allow backspace in insert mode
set backspace=indent,eol,start

" Use spaces instead of tabs
set expandtab

" Set tab width defaults
set tabstop=2
set shiftwidth=2
set softtabstop=2

" Override tab width for certain file types
autocmd FileType make set noexpandtab
autocmd FileType python set tabstop=4
autocmd FileType python set shiftwidth=4
autocmd FileType python set softtabstop=4

" Highlight searches
set hlsearch

" Highlight dynamically as pattern is typed
set incsearch

" Ignore case of searches unless an uppercase character is used
set ignorecase
set smartcase

" Add the g flag to search/replace by default
set gdefault

" Enhance command-line completion
set wildmenu

" Make vim bells visual instead of beeping
set visualbell

" Allow switching edited buffers without saving
set hidden
