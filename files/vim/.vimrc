" Make vim more useful
set nocompatible

" Remap the leader shortcut key to something easier to reach
let mapleader=","

" Disable filetype for Vundle installation
filetype off

" Set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" Let Vundle manage Vundle
Plugin 'gmarik/Vundle.vim'

" Install the Molokai colour scheme
Plugin 'tomasr/molokai'

" Install the CtrlP plugin which allows you to perform a fuzzy search and
" find the file you wish to open
Plugin 'kien/ctrlp.vim'

" Install NERD Tree which provides a nice little file browser
Plugin 'scrooloose/nerdtree'

" Map NERD Tree toggling to Ctrl+n
map <silent> <Leader>n :NERDTreeToggle<CR>

" Install the Syntastic code checker
Plugin 'scrooloose/syntastic'

" Install vim-gitgutter which displays changes in a Git repository on the
" vim sidebar
Plugin 'airblade/vim-gitgutter'

" Install TAGBAR which displays code layout elements in a window
Plugin 'majutsushi/tagbar'

" Install the delimitMate plugin which auto-closes quotes and brackets
Plugin 'Raimondi/delimitMate'

" Complete Vundle initialisation
" (all of your plugins must be added before this line)
call vundle#end()

function! ConfigurePlugins()
  " Set color scheme to molokai
  if filereadable(expand("$HOME/.vim/bundle/molokai/colors/molokai.vim"))
    " Enable the molokai color scheme
    colorscheme molokai

    " Override the line number background color to appear transparent
    hi LineNr ctermbg=234
  endif

  if exists(':SyntasticStatus')
    " Setup the status line to show Syntastic information
    set statusline+=%#warningmsg#
    set statusline+=%{SyntasticStatuslineFlag()}
    set statusline+=%*
  endif
endfunction

" Use the original molokai scheme that's similar to Sublime Text
let g:molokai_original = 1

" Configure how Syntastic runs
let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 0
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0

" Configure our plugins after vim has initialised
autocmd VimEnter * call ConfigurePlugins()

" Enable syntax and file-type highlighting
syntax on
filetype on
filetype plugin on
filetype indent on

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
