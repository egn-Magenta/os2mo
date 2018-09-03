const state = {
  name: undefined,
  uuid: undefined
}

const mutations = {
  change (state, employee) {
    state.name = employee.name
    state.uuid = employee.uuid
  }
}

const getters = {
  getUuid: state => state.uuid,
  get: state => state
}

export default {
  namespaced: true,
  state,
  mutations,
  getters
}
