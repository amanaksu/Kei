/*-------------------------- Document -------------------------------*/
rule OLE
{
    meta:
        author = "amanaksu@gmail.com"
        last_updated = "2018-03-05"
        description = "Compound File Binary Format (DOC, XLS, PPT, HWP 5.x)"
        product = "Microsoft Office, Hangul Editor"

        scan_module = "ole"
        file_type = "ole"
    strings:
        $ole_sig = { D0 CF 11 E0 A1 B1 1A E1 }
    condition:
        $ole_sig at 0
}
/*___________________________________________________________________*/

/*--------------------------- Movie ---------------------------------*/
rule SWF
{
    meta:
        author = "amanaksu@gmail.com"
        last_updated = "2018-03-05"
        description = "detect adobe flash file(SWF)"
        product = "Adobe Flash File"

        scan_module = "swf"
        file_type = "swf"
    strings:
        // SWC, SWF, SWZ signature is offset 0
        $SWC = {43 57 53}
        $SWF = {46 57 53}
        $SWZ = {5A 57 53}

    condition:
        ($SWC at 0) or ($SWF at 0) or ($SWZ at 0)
}
/*___________________________________________________________________*/

/*--------------------------- Image ---------------------------------*/
rule BMP
{
    meta:
        author = "amanaksu@gmail.com"
        last_updated = "2018-03-06"
        description = "detect bitmap file (BMP)"
        
        scan_module = "bmp"
        file_type = "bmp"
    strings:
        $bmp_sig = { 42 4D }    // BM

    condition:
        $bmp_sig at 0
}

rule GIF
{
    meta:
        author = "amanaksu@gmail.com"
        last_updated = "2018-05-03"
        description = "detect graphic interchange format file (GIF)"
        
        scan_module = "gif"
        file_type = "gif"
    strings:
        $gif_sig = { 47 49 46 38 39 61 }    // GIF89a

    condition:
        $gif_sig at 0
}
/*___________________________________________________________________*/

/*------------------------- IoT / Linux -----------------------------*/
rule ELF
{
    meta:
        author = "amanaksu@gmail.com"
        last_updated = "2018-09-12"
        description = "detect elf file (for Linux, IoT)"
        
        scan_module = "elf"
        file_type = "elf"
    strings:
        $elf_sig = { 7F 45 4C 46 }	        // .ELF

    condition:
        $elf_sig at 0	

}
/*___________________________________________________________________*/