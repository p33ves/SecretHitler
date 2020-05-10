

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

bot.on('message', function (user, userID, channelID, message, evt) {
    // Our bot needs to know if it will execute a command
    // It will listen for messages that will start with `!`
    if (message.substring(0, 3) == 'sh!') {
        let args = message.substring(3).split(' ');
        let cmd = args[0];
        let boardState = false;
        let playerList = []

        args = args.splice(1);
        switch(cmd) {
            // sh!test
            case 'test':
                bot.sendMessage({
                    to: channelID,
                    message: dedent(
                        `*The year is 1932. The place is pre-WWII Germany. 
                        In Secret Hitler, players are German politicians attempting to hold a fragile Liberal government together and stem the rising tide of Fascism. 
                        Watch out though— there are secret Fascists among you, and one player is the Secret Hitler.*`)
                });
            break;

            case 'open':
                bot.sendMessage({
                    to: channelID,
                    message:'A board has been opened. Please type sh!join if you wish to join the game.'
                });
                boardState = true;

            case 'join':
                if (boardState) {
                    
                }


            break;
            // Just add any case commands if you want to..
         }
     }
});
