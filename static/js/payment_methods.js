function upifunc() {
    var input = document.getElementById("upi_input");
    var input2 = document.getElementById("bank_input");
    var input3 = document.getElementById("wallet_input");
    if (input.classList.contains("invisible")) {
        input.classList.add("display");
        input.classList.remove("invisible");
        input2.classList.remove("display");
        input2.classList.add("invisible");
        input3.classList.remove("display");
        input3.classList.add("invisible");
    } else {
        input.classList.remove("display");
        input.classList.add("invisible");
    }
}
function bankfunc() {
    var input = document.getElementById("bank_input");
    var input2 = document.getElementById("upi_input");
    var input3 = document.getElementById("wallet_input");
    console.log(document.getElementById("accno"));
    if (input.classList.contains("invisible")) {
        input.classList.add("display");
        input.classList.remove("invisible");
        input2.classList.remove("display");
        input2.classList.add("invisible");
        input3.classList.remove("display");
        input3.classList.add("invisible");
    } else {
        input.classList.remove("display");
        input.classList.add("invisible");
    }
}
function walletfunc() {
    var input = document.getElementById("wallet_input");
    var input2 = document.getElementById("upi_input");
    var input3 = document.getElementById("bank_input");
    if (input.classList.contains("invisible")) {
        input.classList.add("display");
        input.classList.remove("invisible");
        input2.classList.remove("display");
        input2.classList.add("invisible");
        input3.classList.remove("display");
        input3.classList.add("invisible");
    } else {
        input.classList.remove("display");
        input.classList.add("invisible");
    }
}

function empty() {
    var a = document.getElementById("a");
    var b = document.getElementById("b");
    var c = document.getElementById("c");
    var d = document.getElementById("d");
    var e = document.getElementById("e");
    var h = document.getElementById("h");
    var x = document.getElementById("snackbar");
    console.log(a.value != "" || b.value != "" || c.value != "" || d.value != "" || e.value != "" || h.value != "");
    if (a.value != "" || b.value != "" || c.value != "" || d.value != "" || e.value != "" || h.value != "") {
        var form = document.getElementById("form");
        form.submit();
        
    }else {
        var x = document.getElementById("snackbar");
        x.className = "show";
        setTimeout(function(){ x.className = x.className.replace("show", ""); }, 3000);   
    }
}