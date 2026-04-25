(function () {
    'use strict';

    function start() {
        if (window.news_plugin == true)
            return;

        window.news_plugin = true;

        Lampa.Listener.follow('request_before', function (e) {
            if (Lampa.Storage.get('language', '') == 'uk' && e.params.url.indexOf('/feed/all') != -1) {
                e.params.url = 'https://lampa-ua-pack.github.io/news/data.uk.json';
            }
        });

        Lampa.Lang.add({
            "title_in_high_quality": {
                'uk': 'У високій якості',
            }
        });
    }

    if (window.appready) start();
    else {
        Lampa.Listener.follow('app', function (e) {
            if (e.type == 'ready') {
                start();
            }
        });
    }
})();