# dx_xact

`dx_xact` intends to provide a simple interface for manipulating 
[DirectX's XACT audio file formats](https://wiki.multimedia.cx/index.php/XACT).

An MVP would allow for parsing and generation of XACT files programmatically, 
as opposed to being forced to use [old SDKs](https://archive.org/details/dx9sdk) to produce them.

_NOTE:_ This project intends to target DX9 formats in the case that changes were made for DX 10 and 11 - specifically, little-endian version `45`.
I may expand the scope of this to include big-endian formats (for XBOX) and different versions, 
but especially the latter isn't highly likely to happen of my own accord.

## Acknowledgements

This project would not be possible without reference to both [unxwb](https://aluigi.altervista.org/papers.htm#unxwb)
and [MonoGame](https://github.com/MonoGame/MonoGame), with the former providing the prerequisite knowledge for 
both the latter and me to implement this tooling, and the latter providing a much simpler interface to 
improve my understanding of the format (as well as being a syntax I'm *much* more familiar with).

Additionally, all holes in knowledge between these two were resolved by 
[*trigger-segfault's* wiki page from their terraria wave bank tool](https://github.com/trigger-segfault/QuickWaveBank/wiki/Wave-Bank-Format),
giving more than enough information surrounding data placement and types to clean up my code (and refine parsing/writing further).