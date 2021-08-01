document.addEventListener('DOMContentLoaded', () => {
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // remebring channel 
    if (!localStorage.getItem('channel')){
        var channel = document.querySelector('#channels-list').value;
        localStorage.setItem('channel', channel);
        
    }   
    else{
        document.querySelector('#channels-list').value = localStorage.getItem('channel');
        var channel = document.querySelector('#channels-list').value;
    }
        
    function loadmessages() {
        // a function to load messages sent to a channel 
         const request = new XMLHttpRequest;
         request.open('POST', '/channel');

         request.onload = () => {
             const data = JSON.parse(request.response)
             data.forEach(function (msg) {
                 const div = document.createElement('div');
                 const h = document.createElement('h5');
                 const p = document.createElement('p');
                 h.innerHTML = msg.user + ' @ ' + msg.message_time;
                 h.style.color = 'blue';
                 p.innerHTML = msg.messages;
                 div.appendChild(h);
                 div.appendChild(p);
                 var username = document.querySelector('#username').innerHTML;
                 if (msg.user == username) {
                     const btn = document.createElement('button');
                     message_id = msg.message_id;
                     btn.innerHTML = 'x';
                     btn.setAttribute("class", "remove");
                     btn.setAttribute("id", message_id);
                     btn.addEventListener("click", deleteItem, false);
                     div.appendChild(btn);
                 }
                 document.querySelector('#chatbox').appendChild(div);
                 document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
             });


         }
         // Add data to send with request
         const data = new FormData();
         data.append('channel', channel);

         // Send request
         request.send(data);
     }
    
    loadmessages();
    socket.on('connect', () => {
        // send a request to create a channel 
        var button = document.querySelector('#create');
        button.onclick = () => {
            var name = document.getElementById('channel-name').value;
            socket.emit('create channel', {'name': name});
        };
    });

    socket.on('channel name', data => {
        // add the channel created to the channel list 
        const option = document.createElement('option')
        option.innerHTML = data.name;
        document.querySelector('#channels-list').appendChild(option);
        

    });

    socket.on('connect', () => {
        // sending user  messages to th server 
        const button = document.querySelector('#submitmsg')
        button.onclick = () => {
            const message = document.querySelector('#usermsg').value;
            if (message.length != 0) {
                socket.emit('new message', { 'message': message, 'channel': channel });
            }
            
            
        }
    })
    
    socket.on('annonce message', data => {
    // add messages to the channel 
        const div = document.createElement('div');
        const h = document.createElement('h5');
        const p = document.createElement('p');
        h.innerHTML = data.user + ' @ ' + data.message_time; 
        h.style.color = 'blue';
        p.innerHTML = data.message;
        div.appendChild(h);
        div.appendChild(p);
        var username = document.querySelector('#username').innerHTML;
        if (data.user == username ){
        const btn = document.createElement('button');
        btn.innerHTML = 'x';
        message_id = data.message_id;
        btn.setAttribute("class", "remove");
        btn.setAttribute("id", message_id);
        btn.addEventListener("click", deleteItem, false);
        div.appendChild(btn);
        }
        document.querySelector('#chatbox').appendChild(div);
        document.querySelector('#chatbox').scrollTop = document.querySelector('#chatbox').scrollHeight;
    })

    button = document.querySelector('#channels-list');
    button.onchange = () => {
        // change channel and load messages sent there 
        channel = button.value;
        localStorage.setItem('channel', channel);
        const parent = document.querySelector('#chatbox');
        while (parent.firstChild) {
            parent.firstChild.remove();
        }
       loadmessages();

    }
    function deleteItem() {
        // delete messages and sending a signal to the server to delte the message from the memory 
        this.parentNode.parentNode.removeChild(this.parentNode);
        channel = document.querySelector('#channels-list').value;
        message_id = this.id;
        socket.emit('delete message', {'channel': channel, 'message_id': message_id})
       
    };
    
});