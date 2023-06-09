
let user_name=false
let secondaparte=false
let nome_utente=''
let pagine=0
let articoli=0
var dateStrings = [];
var dataset=false
class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }

        this.state = false;
        this.messages = [];
        this.nome_utente=''

    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // show or hides the box
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
    }
    

    onSendButton(chatbox) {
        console.log(user_name)
        let loadInterval;
        const chatmessage = chatbox.querySelector('.chatbox__messages');
        var html1=''
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        let chiocciola= text1.indexOf("@");

        if (text1 === "") {
            return;
        }
        else if (text1.length>0){
            html1 += '<div id="div-02" class="messages__item messages__item--visitor">.</div><div id="div-01" class="messages__item messages__item--operator">' + text1 + '</div>'
            chatmessage.innerHTML = html1 + chatmessage.innerHTML;

        }
        //to make the placeholder empty
        textField.value=''
        //function to load our messages
        let loader= document.getElementById("div-02")
        loadInterval = setInterval(() => {
            loader.textContent += '.';
    
            if(loader.textContent === '.....'){
                loader.textContent='.';
            }
            }, 300)
        if (user_name==false){
            if (chiocciola !== -1){
                user_name=true;
                const parti = text1.split("@");
                if(parti.length > 1) {
                    let nome = parti[1].split(" ")[0];
                    if (nome.endsWith(',') || nome.endsWith('.')) {
                        nome = nome.slice(0, -1);
                        console.log(nome);
                }else{
                    console.log(nome); // "jacopo"
                    const data = null;
                    const xhr = new XMLHttpRequest();
                    xhr.withCredentials = true;
                    xhr.addEventListener('readystatechange', function () {
	                    if (this.readyState === this.DONE) {
		                let risposta=this.responseText;
                        if (risposta.includes('error')){
                            user_name=false;
                            const element = document.getElementById("div-02");
                            element.remove(); // Removes the div with the 'div-02' id
                            html1='<div class="messages__item messages__item--visitor">User not found, could you please type the user name again?</div>'
                            chatmessage.innerHTML = html1 + chatmessage.innerHTML;
                        }else{
                            user_name=true
                            nome_utente=nome
                            console.log(nome_utente)
                            const element = document.getElementById("div-02");
                            element.remove(); // Removes the div with the 'div-02' id
                            console.log(this.responseText)
                            const obj = JSON.parse(this.responseText);
                            const firstName = obj.first_name;
            
                            const items= obj.aggregates.resale_posts;
                            html1='<div class="messages__item messages__item--visitor">Hi ' + firstName+ ', I found you! I see that you have '+ items+ ' item(s) in your closet. Would you like me to analyse them and offer suggestions? <br><br> (it could take up to one minute)</div>'
                            chatmessage.innerHTML = html1 + chatmessage.innerHTML;
                            let n_items= parseInt(items);
                            pagine=Math.ceil(n_items/48)
                            articoli=n_items%48
                            /*
                            console.log(pagine)
                            console.log(articoli)
                            console.log(items)
                            console.log(firstName);*/
                            }
	                    }
                });

                    xhr.open('GET', 'https://poshmark.p.rapidapi.com/user?username='+nome+'&domain=com');
                    xhr.setRequestHeader('X-RapidAPI-Key', '95d2991611msh93424e934624ea0p12c0d5jsnd0a3fc4895d3');
                    xhr.setRequestHeader('X-RapidAPI-Host', 'poshmark.p.rapidapi.com');

                    xhr.send(data);
                    }
                }
            }
            else //If the username is not iserted correctly
            {

                let msg1 = { name: "User", message: text1 }
                this.messages.push(msg1);

                fetch('http://127.0.0.1:5000/user', {
                    method: 'POST',
                    body: JSON.stringify({ message: text1 }),
                    mode: 'cors',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })
                .then(r => r.json())
                .then(r => {
                    let msg2 = { name: "Sam", message: r.answer };
                    this.messages.push(msg2);
                    this.updateChatText(chatbox)
                    textField.value = ''

                }).catch((error) => {
                    console.error('Error:', error);
                    this.updateChatText(chatbox)
                    textField.value = ''
                });
            }
        } else if(dataset==false){
            console.log(dataset)
            dataset=true

            let msg1 = { name: "User", message: text1 }
            this.messages.push(msg1);
            /*var data = null;
            var xhr = new XMLHttpRequest();
            xhr.withCredentials = true;
            xhr.addEventListener('readystatechange', function () {
                if (this.readyState === this.DONE) {
                    console.log(this.responseText);
                    const obj1 = JSON.parse(this.responseText);
                    number_items=obj1.data.length
                //extract a random number to choos the items
                //function getRandomNumber(min, max) {
                //    return Math.floor(Math.random() * (max - min + 1)) + min;
                //  }
                  
                //const randomNumber = getRandomNumber(0, number_items);
                //const item = obj1.data[randomNumber].title;
                //console.log(randomNumber)
                //console.log(obj1.data[randomNumber].description)
                console.log(obj1.data[0].price_amount.val)
                //console.log(obj1.data[randomNumber].first_published_at)
                //console.log(item)
                //creiamo una lista dove contenere tutte le date
                
                //creiamo il for loop
                for (let x = 0; x < articoli; x++) {
                    var datastring=obj1.data[x].first_published_at
                    var date1 = new Date(datastring);
                    
                    dateStrings.push({
                        data: date1,
                        chiave: x,
                      });
                // Ordina le date dal più vecchio al più recente
                dateStrings.sort((a, b) => a.data - b.data);

                // Estrai le prime 5 date più vecchie con la chiave corrispondente
                const oldestDates = dateStrings.slice(0, 5);

                // Stampa i risultati
                console.log("Le 5 date più vecchie con la chiave corrispondente sono:");
                oldestDates.forEach(dateObj => {
                console.log(`Data: ${dateObj.data.toISOString()}, Chiave: ${dateObj.chiave}`);
                console.log(obj1.data[dateObj.chiave].title)
                });

                
                }

            }
        });
        
        xhr.open('GET', 'https://poshmark.p.rapidapi.com/closet?username='+nome_utente+'&page='+pagine+'&domain=com');
        xhr.setRequestHeader('X-RapidAPI-Key', '95d2991611msh93424e934624ea0p12c0d5jsnd0a3fc4895d3');
        xhr.setRequestHeader('X-RapidAPI-Host', 'poshmark.p.rapidapi.com');
        
        xhr.send(data);
    
        
        
setInterval(function(){if(dateStrings){
    console.log(dateStrings)
const element = document.getElementById("div-02");
element.remove(); // Removes the div with the 'div-02' id
html1='<div class="messages__item messages__item--visitor">I analysed your closet and it turned out that you have some products that have not been sold for a long time. For example: <br><br> 1)NWT Lucky Brand Blue AVAMid Rise Crop Jeans Size 8 <br> 2)Guess Safiano Hard cover iPhone 11 Pro Max Black <br> 3)Star Wars The Mandalorian Airpods Case1st AND 2nd <br> 4)Star Wars Disney Stormtrooper 1 &2 AirPods CASE <br>5)NWT Free People Galloon Lace Racerback Green M <br><br>Would you like suggestions to make them more attractive to the market?  </div>'
chatmessage.innerHTML = html1 + chatmessage.innerHTML;
const data1 = null;

const xhr1 = new XMLHttpRequest();
xhr1.withCredentials = true;

xhr1.addEventListener('readystatechange', function () {
	if (this.readyState === this.DONE) {
		console.log(this.responseText);
	}
});

xhr1.open('GET', 'https://poshmark.p.rapidapi.com/search?query=Patricia%20Nash%20Bag&domain=com');
xhr1.setRequestHeader('Accept-Encoding', 'gzip, deflate');
xhr1.setRequestHeader('X-RapidAPI-Key', '95d2991611msh93424e934624ea0p12c0d5jsnd0a3fc4895d3');
xhr1.setRequestHeader('X-RapidAPI-Host', 'poshmark.p.rapidapi.com');

xhr1.send(data);
secondaparte=true
}

}, 4000)*/




        

        

        fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            body: JSON.stringify({ message: nome_utente, items: pagine }),
            mode: 'cors',
            headers: {
              'Content-Type': 'application/json'
            },
          })
          .then(r => r.json())
          .then(r => {
            let msg2 = { name: "Sam", message: r.answer };
            this.messages.push(msg2);
            this.updateChatText(chatbox)
            textField.value = ''

        }).catch((error) => {
            console.error('Error:', error);
            this.updateChatText(chatbox)
            textField.value = ''
          });
    
    


    
}
else{
    let msg1 = { name: "User", message: text1 }
    this.messages.push(msg1);
    
    var previous=document.getElementsByClassName('messages__item messages__item--visitor')
    var previous_message1=previous[1]
    var previous_message=previous_message1.textContent

    fetch('http://127.0.0.1:5000/query', {
        method: 'POST',
        body: JSON.stringify({ message: text1, message1:previous_message }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(r => r.json())
    .then(r => {
        let msg2 = { name: "Sam", message: r.answer };
        this.messages.push(msg2);
        this.updateChatText(chatbox)
        textField.value = ''

    }).catch((error) => {
        console.error('Error:', error);
        this.updateChatText(chatbox)
        textField.value = ''
    });
}
}

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice(-2).reverse().forEach(function(item, index) {
            if (item.name === "Sam")
            {
                
                var testo_modificato = item.message.replace(" 1)", "<br><br><br>1)")
                
                testo_modificato = item.message.replace(" 1.", "<br><br><br>1)")
                testo_modificato=testo_modificato.replace("Would you like suggestions","<br><br><br>Would you like suggestions")
                testo_modificato=testo_modificato.replace(" 2)", "<br>2)")
                testo_modificato=testo_modificato.replace(" 3)", "<br>3)")
                testo_modificato=testo_modificato.replace(" 4)", "<br>4)")
                testo_modificato=testo_modificato.replace(" 5)", "<br>5)")
                testo_modificato=testo_modificato.replace(" 2.", "<br>2)")
                testo_modificato=testo_modificato.replace(" 3.", "<br>3)")
                testo_modificato=testo_modificato.replace(" 4.", "<br>4)")
                testo_modificato=testo_modificato.replace(" 5.", "<br>5)")
                
                html += '<div class="messages__item messages__item--visitor">' + testo_modificato + '</div>'
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
          });
        const element1=document.getElementById("div-01");
        const element = document.getElementById("div-02");
        element.remove(); // Removes the div with the 'div-02' id
        element1.remove()

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html + chatmessage.innerHTML;
    }
}


const chatbox = new Chatbox();
chatbox.display();
