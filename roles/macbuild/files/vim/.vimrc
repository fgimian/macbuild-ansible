" Make vim more useful
set nocompatible

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

" Enable syntax highlighting
syntax on

" Override the line number background color to appear transparent
hi LineNr ctermbg=234

" Show the cursor position
set ruler

" Set the long-line marker
set colorcolumn=80

" Enable smart indent
set smartindent

" Allow backspace in insert mode
set backspace=2

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

" Ignore case of searches
set ignorecase

" Add the g flag to search/replace by default
set gdefault

" Enhance command-line completion
set wildmenu
