import { createStore } from 'vuex'

const store = createStore({
    state(){
        return{
            asideWidth: "250px"
        }
    },
    mutations:{
        handleAsideWidth(state){
            state.asideWidth = state.asideWidth == "250px" ? "64px" : "250px"
        }
    },
    actions:{

    }
})

export default store