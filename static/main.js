function sign_out() {
    //token을 버릴거야~ 라고 할떄, (자유이용권을 버린다고 할때) .removeCookie라는 jquery함수를 사용함
    $.removeCookie('mytoken', {path: '/'});
    alert('ログアウト!')
    window.location.href = "/"
}

function checking() {

    let department = '{{department}}'
    let name = '{{name}}'
    // let today = new Date().toString('%Y-%m-%d-%H-%M-%S')

    $.ajax({
        url: '/checking',
        type: 'POST',
        data: {
            department_give: department,
            name_give: name,
        },
        success: function (response) {
            alert(response['msg'])
            window.location.reload()
        }
    })
}

function listing() {
    $.ajax({
        type: 'GET',
        url: '/listing',
        data: {},
        success: function (response) {
            let list = response['listing']
            for (let i = 0; i < list.length; i++) {
                let check_time = list[i]['date']
                let department = list[i]['department']
                let name = list[i]['name']
                let check = list[i]['check']
                let list_html = `
                                            <tr>
                                                <td>${department}</td>
                                                <td>${name}</td>
                                                <td>${check_time}</td>
                                                <td>${check}</td>
                                            </tr>
                                        `

                $('.table_list').append(list_html)

                if (check == '遅刻') {
                    let check_list = `
                                        <div class = "check_name">${name}&nbsp</div>
                                                `
                    $('.check_person').append(check_list)
                }
            }

        }
    })
}