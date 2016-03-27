" Make vim more useful
set nocompatible

" Remap the leader shortcut key to something easier to reach
let mapleader = ","

" Disable filetype for Vundle installation
filetype off

" Set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" Let Vundle manage Vundle
Plugin 'gmarik/Vundle.vim'

" Install the Molokai color scheme
Plugin 'tomasr/molokai'

" Install the CtrlP plugin which allows you to perform a fuzzy search and
" find the file you wish to open
Plugin 'kien/ctrlp.vim'

" Install NERD Tree which provides a nice little file browser
Plugin 'scrooloose/nerdtree'

" Map NERD Tree toggling to Ctrl+n
map <silent> <Leader>n :NERDTreeToggle<CR>

" Install fugitive for better git support
Plugin 'tpope/vim-fugitive'

" Install vim-gitgutter which displays changes in a Git repository on the
" vim sidebar
Plugin 'airblade/vim-gitgutter'

" Install TAGBAR which displays code layout elements in a window
Plugin 'majutsushi/tagbar'

" Enables new-line and indentation of matched item pairs
let delimitMate_expand_cr = 1

" Enables trailing space to be added for matched item pairs
let delimitMate_expand_space = 1

" Install the delimitMate plugin which auto-closes quotes and brackets
Plugin 'Raimondi/delimitMate'

" Enable neocomplete on startup
let g:neocomplete#enable_at_startup = 1

" Automatically select the first item in neocomplete completions
let g:neocomplete#enable_auto_select = 1

" Start autocompleting with neocomplete after a single character is typed
let g:neocomplete#auto_completion_start_length = 1

" Install neocomplete for completions
Plugin 'Shougo/neocomplete'

" Allow the tab key to autocomplete neocomplete suggestions
inoremap <expr><TAB> pumvisible() ? "\<ENTER>" : "\<TAB>"

" Disable split window preview of functions as you type for neocomplete
set completeopt-=preview

" Install coffeescript support
Plugin 'kchmck/vim-coffee-script'

" Install better Javascript support
Plugin 'pangloss/vim-javascript'

" Install tabularize for aligning code
Plugin 'godlygeek/tabular'

" Enable visibility of all open files with airline
let g:airline#extensions#tabline#enabled = 1

" Enable powerline fonts for airline
let g:airline_powerline_fonts = 1

" Use the tomorrow theme for airline
let g:airline_theme = 'powerlineish'

" Install the airline plugin for a really nice and informative status bar
Plugin 'bling/vim-airline'

" Install emmet for awesome HTML writing magic
Plugin 'mattn/emmet-vim'

" Disable indent guides on start as they often may not be needed, they may be
" enabled manually using the :IndentGuidesEnable command
let g:indent_guides_enable_on_vim_startup = 0

" Only use a single character to show indent guides
let g:indent_guides_guide_size = 1

" Enable custom indent guide colors
let g:indent_guides_auto_colors = 0

" Install vim-indent-guides for indent guides
Plugin 'nathanaelkane/vim-indent-guides'

" Complete Vundle initialisation
" (all of your plugins must be added before this line)
call vundle#end()

function! ConfigurePlugins()
  " Set colors to match the molokai scheme
  if filereadable(expand("$HOME/.vim/bundle/molokai/colors/molokai.vim"))
    " Override the line number background color to appear transparent
    hi LineNr ctermbg=234

    " Set indent guide background colors
    hi IndentGuidesOdd ctermbg=235
    hi IndentGuidesEven ctermbg=235
  endif
endfunction

" Use the original molokai scheme that's similar to Sublime Text
let g:molokai_original = 1

" Set color scheme to molokai
if filereadable(expand("$HOME/.vim/bundle/molokai/colors/molokai.vim"))
  colorscheme molokai
endif

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

" Allow Shift+Tab to un-indent at the cursor
inoremap <S-TAB> <C-d>
