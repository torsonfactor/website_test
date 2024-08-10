

                var evt = new Event(),
                    m = new Magnifier(evt);
                    m.attach({
                        thumb: '#thumb',
                        large: "{{product.photo.url}}",
                        largeWrapper: 'preview',
                        zoom: 3,
                    });

                var evt = new Event(),
                    m = new Magnifier(evt, {
                        zoom: 3,
                        zoomable: true,
                    });

                m.attach({
                    thumb: '#thumb',
                    large: '{{product.photo.url}}',
                    largeWrapper: 'preview',
                    zoom: 2,
                    zoomable: true,
                    onthumbenter: function () {
                        document.getElementById('enter').innerHTML = 'Mouse enter';
                        document.getElementById('leave').innerHTML = '';
                        document.getElementById('zoom').innerHTML = '';
                    },
                    onthumbmove: function () {
                        document.getElementById('move').innerHTML = 'Mouse move';
                    },
                    onthumbleave: function () {
                        document.getElementById('enter').innerHTML = '';
                        document.getElementById('move').innerHTML = '';
                        document.getElementById('zoom').innerHTML = '';
                        document.getElementById('leave').innerHTML = 'Mouse leave';
                    },
                    onzoom: function (data) {
                        document.getElementById('zoom').innerHTML = 'Zoom: ' + data.zoom;
                    }
                });




