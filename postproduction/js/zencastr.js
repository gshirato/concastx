function get_episode_name () {
    /**
     * @returns {string}
     */
    var URL_elems = document.URL.split('/')
    return URL_elems[URL_elems.length - 1]
}

function footnote_to_csv() {
    /**
     * @returns {string}
     */
    var offset_time = prompt('ずらす時間は?', '0:00:00')
    var delim = '	'
    var fns = document.querySelectorAll('.footnote')
    var csv_str = 'Name	Start' + delim + 'Duration' + delim + 'Time Format' + delim + 'Type' + delim + 'Description\n'
    var offset_array = offset_time.split(':').map(t=>+t)

    for (let i = 0; i < fns.length; i++) {
        var footnote = fns[i].children[1]
        var text = footnote.querySelector('.text').innerText
        var time = footnote.querySelector('.time').innerText.replace('h ', ':').replace('m ', ':').replace('s', '')
        var time_array = time.split(':').map(t=>+t)
        var time_object = new Date(0, 0, 0, time_array[0], time_array[1], time_array[2])

        time_object.setHours(time_object.getHours() +  offset_array[0])
        time_object.setMinutes(time_object.getMinutes() +  offset_array[1])
        time_object.setSeconds(time_object.getSeconds() +  offset_array[2])

        var sum_str = time_object.getHours() + ':' + time_object.getMinutes() + ':' + time_object.getSeconds()

        /*var diff = time_object - offset_time_object
        var hours = Math.floor(diff / 1000 / 60 / 60);
        diff -= hours * 1000 * 60 * 60;
        var minutes = Math.floor(diff / 1000 / 60);
        diff -= minutes * 1000 * 60
        var seconds = Math.floor(diff / 1000)
        var diff_str = hours + ':' + minutes + ':' + seconds
        */

        csv_str += text + delim + sum_str + delim + '0:00:00' + delim + 'decimal' + delim + 'Cue' + delim + '\n'
    }
    let blob = new Blob([csv_str],{type:"text/csv"});
        let link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = get_episode_name() + '.csv'
        link.click()
}

footnote_to_csv()