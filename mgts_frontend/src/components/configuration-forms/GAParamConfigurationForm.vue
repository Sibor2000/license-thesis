<template>

    <button class="button" @click="addGAParamConfig()">
        Add configuration
    </button>

    <div class="table-box" v-if="gaParams && gaParams.length">
        <table border="1" class="param-table">
            <thead>
                <tr>
                    <th v-for="(paramField, index) in paramFields" class="param-table-cell param-table-header">
                        {{ paramField.name }}
                    </th>
                    <th class="param-table-cell param-table-header"></th>
                </tr>
            </thead>

            <tbody :key="tableKey">
                <tr v-for="(param, rowIndex) in gaParams" :key="rowIndex">
                    <td v-for="(field, colIndex) in paramFields" :key="colIndex" class="param-table-cell">
                        <input v-if="field.type === 'string' && !getOptionsForField(field.name).length" type="text"
                            v-model="gaParams[rowIndex][field.name]" class="small-input" />

                        <input v-else-if="field.type === 'int' || field.type === 'float'" type="number"
                            v-model.number="gaParams[rowIndex][field.name]" class="small-input" />

                        <select v-else v-model="gaParams[rowIndex][field.name]" class="small-input">
                            <option v-for="option in getOptionsForField(field.name)" :key="option" :value="option">
                                {{ option }}
                            </option>
                        </select>
                    </td>

                    <td class="param-table-cell">
                        <button class="button" @click="removeGAParamConfig(rowIndex)">
                            Remove
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>

export default {
    name: 'GAParamConfigurationForm',
    data() {
        return {
            paramFields: [
                { name: "id", type: "string" },
                { name: "pop_size", type: "int" },
                { name: "pc", type: "float" },
                { name: "pm", type: "float" },
                { name: "sel", type: "string" },
                { name: "cros", type: "string" },
                { name: "mp", type: "bool" },
                { name: "mut", type: "string" },
                { name: "ss", type: "bool" },
                { name: "ep", type: "int" },
            ],
            tableKey: 0
        }
    },
    props: {
        gaParams: {
            type: Array,
            required: true
        }
    },
    emits: ['update:gaParams'],
    watch: {
        localGAParams: {
            handler(newVal) {
                this.$emit('update:gaParams', JSON.parse(JSON.stringify(newVal)));
            },
            deep: true
        }
    },
    methods: {
        addGAParamConfig() {
            const newParam = {};
            this.paramFields.forEach(field => {
                const fieldName = field.name

                if (fieldName === 'id') {
                    newParam[fieldName] = 'Default';
                } else if (['float','int'].includes(field.type)) {
                    newParam[fieldName] = 0;
                } else {
                    const options = this.getOptionsForField(fieldName);
                    newParam[fieldName] = options[0] || '';
                }


            });
            this.$emit('update:gaParams', [...this.gaParams, newParam]);
            this.tableKey++;
        },
        removeGAParamConfig(index) {
            const updated = [...this.gaParams];
            updated.splice(index, 1);
            this.$emit('update:gaParams', updated);
        },
        getOptionsForField(field) {
            const optionsMap = {
                sel: ["roulette", "tournament"],
                cros: ["one_point", "multi_points", "uniform", "arithmetic"],
                mp: [true, false],
                mut: ["flip", "swap"],
                ss: [true, false]
            };
            return optionsMap[field] || [];
        }
    }
}

</script>

<style></style>