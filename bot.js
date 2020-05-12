// @ts-check

const Discord = require('discord.io');
const logger = require('winston');
const auth = require('./auth.json');


function dedent(callSite, ...args) {

    function format(str) {
        let size = -1;
        return str.replace(/\n(\s+)/g, (m, m1) => {

            if (size < 0)
                size = m1.replace(/\t/g, "    ").length;
            return "\n" + m1.slice(Math.min(m1.length, size));
        });
    }

    if (typeof callSite === "string")
        return format(callSite);

    if (typeof callSite === "function")
        return (...args) => format(callSite(...args));

    let output = callSite
        .slice(0, args.length + 1)
        .map((text, i) => (i === 0 ? "" : args[i - 1]) + text)
        .join("");

    return format(output);
}


// Configure logger settings
logger.remove(logger.transports.Console);
logger.add(new logger.transports.Console, {
    colorize: true
});
logger.level = 'debug';

// Initialize Discord Bot
let bot = new Discord.Client({
    token: auth.token,
    autorun: true
});
bot.on('ready', function (evt) {
    logger.info('Connected');
    logger.info('Logged in as: ');
    logger.info(bot.username + ' - (' + bot.id + ')');
});

let boardState = false;
let playerList = {}// 
let dummyPlayerList = {
    '0444': 'adois',
    '0333': 'deepak',
    '0999': 'arvindh',
    '0707': 'sandjae'
}

let messageIDmap = {};

let fullDetailsOfPlayer = []; // {userId:'id', name:'name', role:'role'}

const dispNames = (playerList) => Object.values(playerList)
    .map((user, i) => `${i + 1} --- *${user}*`)
    .join('\n')

const randomGenRoles = (count) => {
    let roleArray = ['H', 'L', 'L', 'L', 'F', 'L', 'F', 'L', 'F', 'L'];
    roleArray.splice(count);
    return roleArray.sort((a, b) => 0.5 - Math.random());
}


function sendRoles(playerList, channelID) {
    const count = Object.keys(playerList).length
    const roles = randomGenRoles(count); // ['F', 'L' , 'H' ]
    fullDetailsOfPlayer = Object.keys(playerList).map((playerId, i) => ({ playerId, name: playerList[playerId], role: roles[i] }))
    console.log(fullDetailsOfPlayer)
    fullDetailsOfPlayer.map((player) => {
        bot.sendMessage({
            to: player.playerId,
            message: `Your role is ***${player.role}***.`
        })
    }
    )
}

bot.on('message', function (user, userID, channelID, message, evt) {
    // Our bot needs to know if it will execute a command
    // It will listen for messages that will start with `!`
    if (message.substring(0, 3) == 'sh!') {
        let args = message.substring(3).split(' ');
        let cmd = args[0];


        args = args.splice(1);
        switch (cmd) {
            // sh!test
            case 'test':
                bot.uploadFile({
                    to: channelID,
                    file: './images/SecretHitler_icon25percent.png',
                    message: '>>> ***\tWelcome to Secret Hitler!***'
                });
                break;

            case 'open':
                /* bot.uploadFile({
                    to: channelID,
                    file: './images/SecretHitler_icon25percent.png',
                    message: '>>> ***\t Welcome to Secret Hitler!***'
                }, _ => {
                    bot.sendMessage({
                        to: channelID,
                        message:'\n A board has been opened. Please type sh!join if you wish to join the game.'
                    })
                }); */

                let numofPlayers = 0;

                bot.sendMessage({
                    to: channelID,
                    embed: {
                        color: 1752220,
                        title: '**Players**',
                        description: `A board has been opened. Please type sh!join if you wish to join the game.`
                    }
                }, function (err, res) {
                    messageIDmap.openBoard = res.id;
                });

                boardState = true;

                break;

            case 'join':
                if (boardState) {
                    playerList[userID] = user;
                    bot.editMessage({
                        channelID: channelID,
                        messageID: messageIDmap.openBoard,
                        embed: {
                            color: 1752220,
                            title: '**Players joining this game**',
                            description: `A board has been opened. Please type sh!join if you wish to join the game. \n ${dispNames(playerList)}`
                        }
                    });
                }
                else {
                    bot.sendMessage({
                        to: channelID,
                        message: 'Board has not been opened yet. Please type sh!open to a game first.'
                    });
                }
                console.log(playerList);


                break;

            case 'begin':
                if (boardState && Object.keys(playerList).length > 4 && Object.keys(playerList).length < 11) {
                    bot.sendMessage({
                        to: channelID,
                        message: dedent(
                            `*The year is 1932. The place is pre-WWII Germany. 
                            In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. 
                            Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler.*`)
                    });
                }
                else {
                    if (Object.keys(playerList).length < 5) {
                        bot.sendMessage({
                            to: channelID,
                            message: 'Sorry, but the game requires atleast 5 players!'
                        });
                    }
                    else if (Object.keys(playerList).length > 10) {
                        bot.sendMessage({
                            to: channelID,
                            message: 'Sorry, too many players. Maximum player limit per game is 10!'
                        });
                    }
                    else {
                        bot.sendMessage({
                            to: channelID,
                            message: 'Board has not been opened yet. Please type sh!open to a game first.'
                        });
                    }
                    //boardState = false;
                }

                break;

            case 'begin-test':
                if (boardState) {
                    bot.sendMessage({
                        to: channelID,
                        message: dedent(
                            `*The year is 1932. The place is pre-WWII Germany. 
                            In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. 
                            Watch out though— there are secret Fascists among you, and one of them is the Secret Hitler.*`)
                    });
                    playerList = { ...playerList, ...dummyPlayerList };
                    sendRoles(playerList, channelID);
                }
                break;





            // Just add any case commands if you want to..
        }
    }
});
