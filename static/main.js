class Data {
    constructor(server_data){
        if(!localStorage.data){
            if(server_data != "not_logged") {
                this.data = JSON.parse(server_data);
                localStorage.data = server_data;
            }
            else {
                this.data = {};
                this.save()
            }
        }
        else{
            if(server_data != "not_logged") {
                if(server_data.length > localStorage.data.length){
                    this.data = JSON.parse(server_data);
                    this.save();
                }
                else {
                    this.data=JSON.parse(localStorage.data);
                }
            }
            else {
                this.data=JSON.parse(localStorage.data);
            }
        }
    }
    addDay(date,trees){
        if(trees==""){
            this.data[date]=0
        }
        else{
            if(Number(trees)<10000 && Number(trees)>0){
                this.data[date]=trees;
            }
        }
    }
    delDay(date){
        delete this.data[date]
    }
    compile(){
        return JSON.stringify(this.data)
    }
    save(){
        localStorage.data=JSON.stringify(this.data)
        console.log("Saved")
    }
    format(){
        var data_array=[["Day","Date","Trees","Options"]];
        var n=1
        var ordered_dates=Object.keys(this.data).sort()
        for(var i=0;i<ordered_dates.length;i++){
            var delete_button="<button class='btn btn-success' onclick='client.data.delDay("+'"'+String(ordered_dates[i])+'"'+");client.table.innerHTML=client.data.format();client.total_display.innerHTML=client.data.calculate();client.data_input.value=client.data.compile();client.data.save()'>Delete</button>"
            data_array.push([n,ordered_dates[i],this.data[ordered_dates[i]],delete_button])
            n+=1
        }
        return arrTable(data_array)
    }
    calculate(){
        var trees=0;
        for(var date in this.data){
            trees+=Number(this.data[date]);
        }
        return "<strong>Total: </strong>"+String(trees);
    }
}
class Client {
    constructor(element_IDs, server_data) {
        this.lb_button = document.getElementById(element_IDs.lb_button);
        this.date_input = document.getElementById(element_IDs.date_input);
        this.trees_input = document.getElementById(element_IDs.trees_input);
        this.add_button = document.getElementById(element_IDs.add_button);
        this.total_display = document.getElementById(element_IDs.total_display);
        this.table = document.getElementById(element_IDs.table);
        this.data_input = document.getElementById(element_IDs.data_input);


        this.data = new Data(server_data)

        if(!window.navigator.onLine){
            this.lb_button.disabled = true;
        }

        this.date_input.valueAsDate = new Date();
        this.total_display.innerHTML = this.data.calculate();
        this.table.innerHTML = this.data.format();
        this.data_input.value = this.data.compile();

        var _self = this;
    }
    addDay() {
        this.data.addDay(this.date_input.value, this.trees_input.value);
        this.table.innerHTML = this.data.format();
        this.data_input.value = this.data.compile();
        this.data.save();
        this.total_display.innerHTML = this.data.calculate();
    }
}
function arrTable(arr){
    var title_row=arr.shift();
    var table="<table class='table'><tr>";
    for(var i=0;i<title_row.length;i++){
        table+="<th>"+String(title_row[i])+"</th>"
    }
    table+="</tr>";
    for(var i=0;i<arr.length;i++){
        table+="<tr>";
        for(var j=0;j<arr[i].length;j++){
            table+="<td>"+String(arr[i][j])+"</td>";
        }
        table+="</tr>";
    }
    return table+"</table>"
}




