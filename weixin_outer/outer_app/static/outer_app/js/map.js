$(function () {

    var map = new AMap.Map('container', {
        resizeEnable: true,
        zoom: 10,
    });

    map.plugin('AMap.Geolocation', function () {
        var geolocation = new AMap.Geolocation({
            enableHighAccuracy: true,//是否使用高精度定位，默认:true
            timeout: 10000,          //超过10秒后停止定位，默认：无穷大
            maximumAge: 0,           //定位结果缓存0毫秒，默认：0
            convert: true,           //自动偏移坐标，偏移后的坐标为高德坐标，默认：true
            showButton: true,        //显示定位按钮，默认：true
            buttonPosition: 'LB',    //定位按钮停靠位置，默认：'LB'，左下角
            buttonOffset: new AMap.Pixel(10, 56),//定位按钮与设置的停靠位置的偏移量，默认：Pixel(10, 20)
            showMarker: true,        //定位成功后在定位到的位置显示点标记，默认：true
            showCircle: true,        //定位成功后用圆圈表示定位精度范围，默认：true
            panToLocation: true,     //定位成功后将定位到的位置作为地图中心点，默认：true
            zoomToAccuracy: true      //定位成功后调整地图视野范围使定位位置及精度范围视野内可见，默认：false
        });
        geolocation.getCurrentPosition(function (status, result) {
            if (status == "complete") {
                map.setCenter(result.position);
            } else {
                $.toptips(result.message);
            }
        });
        map.addControl(geolocation);
    });

    var marker_list;
    AMapUI.loadUI(['overlay/SimpleMarker', 'misc/MarkerList'], function(SimpleMarker, MarkerList) {
        //创建一个实例
        marker_list = new MarkerList({
            map: map, //关联的map对象
            listContainer: 'myList', //列表的dom容器的节点或者id, 用于放置getListElement返回的内容
            getDataId: function(dataItem, index) {
                //返回数据项的Id
                return dataItem.id;
            },
            getPosition: function(dataItem) {
                //返回数据项的经纬度，AMap.LngLat实例或者经纬度数组
                return [dataItem.longitude, dataItem.latitude];
            },
            getMarker: function(dataItem, context, recycledMarker) {
                var label = String.fromCharCode('A'.charCodeAt(0) + context.index);
                var color;
                if (dataItem.waitman <= 5) {
                    color = 'green'
                }
                else if (dataItem.waitman >= 10) {
                    color = 'red'
                }
                else {
                    color = 'orange'
                }
                if (recycledMarker) {
                    //存在可回收利用的marker,直接setLabel返回
                    recycledMarker.setLabel(label);
                    return recycledMarker;
                }
                //返回一个新的Marker
                return new SimpleMarker({
                    iconLabel: label,
                    iconStyle: color,
                    color: 'green'
                });
            },
            getInfoWindow: function(dataItem, context, recycledInfoWindow) {
                var title = '<h4>' + dataItem.name + '</h4>'
                var tpl = title + '地址:' + dataItem.address + '<br>电话:' + dataItem.telno +
                    '<br>营业时间:' + dataItem.officehours + '<br>排队人数:' + dataItem.waitman +
                    '人<br><a href="/outer_app/online/num/taking/page/?branch_id=' + dataItem.id + '">在线叫号</a>';
                //MarkerList.utils.template支持underscore语法的模板
                var content = MarkerList.utils.template(tpl, {
                    dataItem: dataItem,
                    dataIndex: context.index
                });
                if (recycledInfoWindow) {
                    //存在可回收利用的infoWindow, 直接setContent返回
                    recycledInfoWindow.setContent(content);
                    return recycledInfoWindow;
                }
                //返回一个新的InfoWindow
                return new AMap.InfoWindow({
                    offset: new AMap.Pixel(0, -23),
                    content: content
                });
            },
            getListElement: function(dataItem, context, recycledListElement) {
                var tpl = '<option value=<%- dataItem.id %> county=<%= dataItem.county %>><%- dataItem.name %></option>';
                var content = MarkerList.utils.template(tpl, {
                    dataItem: dataItem,
                    dataIndex: context.index
                });
                if (recycledListElement) {
                    //存在可回收利用的listElement, 直接更新内容返回
                    recycledListElement.innerHTML = content;
                    return recycledListElement;
                }
                //返回一段html，MarkerList将利用此html构建一个新的dom节点
                return content;
            }
        });
        //监听选中改变
        marker_list.on('selectedChanged', function(event, info) {});
        function forcusMarker(marker) {
            marker.setTop(true);
            //不在地图视野内
            if (!(map.getBounds().contains(marker.getPosition()))) {
                //移动到中心
                map.setCenter(marker.getPosition());
            }
        }
        //监听Marker和ListElement上的点击，详见markerEvents，listElementEvents
        marker_list.on('markerClick listElementClick', function(event, record) {});
        init_data();
    });

    function init_data(){
        $.post(url_pre + '/map/branch/data/', function(resp){
            console.log(resp.counties);
            if(resp.success){
                $.each(resp.counties, function(index, value, array){
                    console.log(value);
                    $('select#count_select').append('<option value="' + value + '">' +value + '</option>');
                });
                marker_list.render(resp.branches);
            }else{
                $.toptips(resp.msg);
            }
        }).error(function(){
            $.toptips('服务器错误');
        });
    }

    $('select#count_select').on('change', function(){
        county = $(this).val();
        console.log(county);
        if(county == '-1'){
            $('select#myList option').each(function(index, ele){
                $(this).show();
            });
        }else{
            $('select#myList').val('-1');
            $('select#myList option').each(function(index, ele){
                if($(this).attr('county') == county){
                    $(this).show();
                }else{
                    $(this).hide();
                }
            });
        }
    });

    $('select#myList').on('change', function(){
        branch_id = parseInt($(this).val());
        if(branch_id != -1){
            record = marker_list.selectByDataId(branch_id);
            console.log(record);
        }
    });
});
