const copy = (id) => { 
    const text = document.getElementById(id).innerHTML;
    const textArea = document.createElement("textarea"); 
    textArea.value=text; document.body.appendChild(textArea); 
    textArea.focus();
    textArea.select(); 
    try{
        document.execCommand('copy');
        var x = document.getElementById("snackbar");

        // Add the "show" class to DIV
        x.className = "show";

        // After 3 seconds, remove the show class from DIV
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);
    }
    catch(err){
        console.error('Unable to copy to clipboard',err)}document.body.removeChild(textArea)
    };

const copyToClipboard = (content) => {
  if (window.isSecureContext && navigator.clipboard) {
    navigator.clipboard.writeText(content);
  } else {
    unsecuredCopyToClipboard(content);
  }
}