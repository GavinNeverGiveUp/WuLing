<template>
  <div class="mgmt-page">
    <AppSidebar active-nav="mgmt" @logout="handleLogout" />

    <main class="mgmt-main">
      <header class="mgmt-header">
        <div>
          <h1>家庭与物资管理</h1>
          <p>在一个页面里查看家庭、管理成员，并维护当前家庭的全部物资。</p>
        </div>
        <div class="header-actions">
          <span class="summary-chip">{{ families.length }} 个家庭</span>
          <BaseButton variant="primary" :disabled="isCreatingFamily" @click="openFamilyModal">
            {{ isCreatingFamily ? '创建中...' : '创建家庭' }}
          </BaseButton>
          <BaseButton variant="ghost" :disabled="isLoadingFamilies || isLoadingItems" @click="refreshAll">刷新数据</BaseButton>
        </div>
      </header>

      <BasePanel class="family-panel" title="我的家庭" description="点击卡片切换到家庭物资详情。">
        <BaseEmptyState v-if="isLoadingFamilies" text="家庭列表加载中..." />
        <BaseEmptyState v-else-if="families.length === 0" :rich="true">
          <span>你还没有加入任何家庭，先创建一个新的家庭开始管理吧。</span>
          <BaseButton variant="primary" :disabled="isCreatingFamily" @click="openFamilyModal">
            立即创建家庭
          </BaseButton>
        </BaseEmptyState>
        <div v-else class="family-grid">
          <article
            v-for="(family, index) in families"
            :key="family.id"
            class="family-card"
            :class="{ active: family.id === selectedFamilyId }"
            @click="selectFamily(family.id)"
          >
            <div class="family-cover" :style="getFamilyCoverStyle(index)">
              <span class="cover-leaf leaf-left">❋</span>
              <span class="cover-leaf leaf-right">❋</span>
            </div>

            <div class="family-card-body">
              <div class="family-card-top">
                <div class="family-title-wrap">
                  <div class="family-title-row">
                    <h3>{{ family.name }}</h3>
                    <span v-if="family.is_default" class="badge badge-default">默认家庭</span>
                    <span v-if="family.role === 'owner'" class="badge badge-owner">Owner</span>
                  </div>
                  <p class="family-meta">
                    <span>{{ family.role === 'owner' ? '你正在守护这个家园' : '你是这个家庭的协作成员' }}</span>
                  </p>
                </div>

                <div class="family-menu-wrap" @click.stop>
                  <button
                    type="button"
                    class="menu-trigger"
                    aria-label="更多操作"
                    @click="toggleFamilyMenu(family.id)"
                  >
                    <img
                      class="icon-img"
                      src="https://api.iconify.design/solar/menu-dots-bold.svg?color=%236b7280"
                      alt=""
                      aria-hidden="true"
                    >
                  </button>

                  <div v-if="activeFamilyMenuId === family.id" class="family-menu">
                    <button
                      type="button"
                      class="family-menu-item"
                      :disabled="family.is_default"
                      @click="setDefaultFamily(family)"
                    >
                      {{ family.is_default ? '当前已是默认家庭' : '设为默认家庭' }}
                    </button>
                    <button
                      v-if="family.role === 'owner'"
                      type="button"
                      class="family-menu-item"
                      :disabled="isManagingFamilyId === family.id"
                      @click="openMembersPanel(family)"
                    >
                      {{ isManagingFamilyId === family.id ? '成员加载中...' : '管理成员' }}
                    </button>
                    <button
                      type="button"
                      class="family-menu-item danger"
                      :disabled="isDeletingFamilyId === family.id"
                      @click="removeFamily(family)"
                    >
                      {{ isDeletingFamilyId === family.id ? '删除中...' : '删除家庭' }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="family-desc">
                这是一个充满生活气息的小世界。
              </div>
            </div>
          </article>
        </div>
      </BasePanel>

      <BasePanel
        class="inventory-panel"
        :title="selectedFamily ? selectedFamily.name : '当前家庭'"
        :description="selectedFamily ? '以下是当前家庭的全部物资。' : '请选择一个家庭查看物资。'"
        :header-center="true"
      >
        <template #extra>
          <div class="panel-actions">
            <BaseButton variant="ghost" :disabled="!selectedFamily || isLoadingItems" @click="loadItems">刷新物资</BaseButton>
            <BaseButton variant="primary" :disabled="!selectedFamily" @click="openItemModal()">新增物资</BaseButton>
          </div>
        </template>
        <BaseEmptyState v-if="!selectedFamily" text="先从上面的家庭卡片中选择一个家庭。" />
        <BaseEmptyState v-else-if="isLoadingItems" text="物资列表加载中..." />
        <BaseEmptyState v-else-if="filteredItems.length === 0" text="这个家庭还没有物资，点击右上角“新增物资”开始添加。" />
        <div v-else class="table-wrap">
          <table class="inventory-table">
            <thead>
              <tr>
                <th>名称</th>
                <th>描述</th>
                <th>位置</th>
                <th>到期时间</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredItems" :key="item.id">
                <td>{{ item.name || '-' }}</td>
                <td>{{ item.description || '-' }}</td>
                <td>{{ item.location || '-' }}</td>
                <td>{{ formatDate(item.expiration_date) }}</td>
                <td>{{ formatDate(item.created_at) }}</td>
                <td>
                  <div class="row-actions">
                    <BaseButton variant="text" @click="openItemModal(item)">编辑</BaseButton>
                    <BaseButton variant="danger" @click="deleteItem(item)">删除</BaseButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </BasePanel>
    </main>

    <BaseModal v-model="showMembersPanel" title="成员管理" :description="managingFamily?.name || ''" width="760px" @close="closeMembersPanel">
        <BaseEmptyState v-if="isLoadingMembers" text="成员列表加载中..." />
        <BaseEmptyState v-else-if="members.length === 0" text="这个家庭暂时没有成员数据。" />
        <div v-else class="member-list">
          <article v-for="member in members" :key="member.id" class="member-card">
            <div>
              <strong>{{ member.username }}</strong>
              <p>{{ member.email || member.phone || '未填写联系方式' }}</p>
            </div>
            <div class="member-actions">
              <select :value="member.role" @change="changeMemberRole(member, $event)">
                <option value="member">member</option>
                <option value="owner">owner</option>
              </select>
              <BaseButton variant="danger" :disabled="member.id === currentUserId" @click="removeMember(member)">
                移出家庭
              </BaseButton>
            </div>
          </article>
        </div>
    </BaseModal>

    <BaseModal
      v-model="showItemModal"
      :title="itemForm.id ? '编辑物资' : '新增物资'"
      :description="selectedFamily?.name || ''"
      @close="closeItemModal"
    >
        <form class="item-form" @submit.prevent="submitItem">
          <BaseFormField label="名称">
            <input v-model.trim="itemForm.name" type="text" maxlength="80" placeholder="例如：婴儿奶粉">
          </BaseFormField>
          <BaseFormField label="描述">
            <textarea v-model.trim="itemForm.description" rows="3" maxlength="240" placeholder="补充说明这件物品的规格、用途或注意事项"></textarea>
          </BaseFormField>
          <BaseFormField label="存放位置">
            <input v-model.trim="itemForm.location" type="text" maxlength="120" placeholder="例如：厨房右侧第二层">
          </BaseFormField>
          <BaseFormField label="到期时间">
            <input v-model="itemForm.expiration_date" type="datetime-local">
          </BaseFormField>

          <div class="form-actions">
            <BaseButton variant="ghost" @click="closeItemModal">取消</BaseButton>
            <BaseButton variant="primary" native-type="submit" :disabled="isSubmittingItem">{{ isSubmittingItem ? '提交中...' : '保存物资' }}</BaseButton>
          </div>
        </form>
    </BaseModal>

    <BaseModal v-model="showFamilyModal" title="创建家庭" description="创建后你会自动成为该家庭的 owner。" @close="closeFamilyModal">
        <form class="item-form" @submit.prevent="submitFamily">
          <BaseFormField label="家庭名称">
            <input v-model.trim="familyForm.name" type="text" maxlength="60" placeholder="例如：三口之家">
          </BaseFormField>

          <div class="form-actions">
            <BaseButton variant="ghost" @click="closeFamilyModal">取消</BaseButton>
            <BaseButton variant="primary" native-type="submit" :disabled="isCreatingFamily">
              {{ isCreatingFamily ? '创建中...' : '确认创建' }}
            </BaseButton>
          </div>
        </form>
    </BaseModal>

    <BaseConfirmDialog
      v-model="showDeleteItemConfirm"
      title="删除物资"
      description="这项操作不可撤销，请确认是否继续。"
      confirm-text="确认删除"
      loading-text="删除中..."
      :loading="isDeletingItem"
      :danger="true"
      @close="closeDeleteItemConfirm"
      @confirm="confirmDeleteItem"
    >
      <p>
        确认删除物资
        <strong>{{ deletingItem?.name || '' }}</strong>
        吗？
      </p>
    </BaseConfirmDialog>

    <BaseConfirmDialog
      v-model="showDeleteFamilyConfirm"
      title="删除家庭"
      description="删除后该家庭下的物资也会一并清空，请确认是否继续。"
      confirm-text="确认删除"
      loading-text="删除中..."
      :loading="Boolean(isDeletingFamilyId)"
      :danger="true"
      @close="closeDeleteFamilyConfirm"
      @confirm="confirmDeleteFamily"
    >
      <p>
        确认删除家庭
        <strong>{{ deletingFamily?.name || '' }}</strong>
        吗？
      </p>
    </BaseConfirmDialog>

    <BaseConfirmDialog
      v-model="showRemoveMemberConfirm"
      title="移出成员"
      description="移出后该成员将不再属于当前家庭。"
      confirm-text="确认移出"
      loading-text="移出中..."
      :loading="isRemovingMember"
      :danger="true"
      @close="closeRemoveMemberConfirm"
      @confirm="confirmRemoveMember"
    >
      <p>
        确认将
        <strong>{{ removingMember?.username || '' }}</strong>
        移出当前家庭吗？
      </p>
    </BaseConfirmDialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { message } from 'ant-design-vue'
import AppSidebar from '@/components/AppSidebar.vue'
import request from '@/utils/request'
import familyCover1 from '@/assets/family_1.png'
import familyCover2 from '@/assets/family_2.png'
import familyCover3 from '@/assets/family_3.png'
import BaseConfirmDialog from '@/components/BaseConfirmDialog.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseEmptyState from '@/components/BaseEmptyState.vue'
import BaseFormField from '@/components/BaseFormField.vue'
import BaseModal from '@/components/BaseModal.vue'
import BasePanel from '@/components/BasePanel.vue'

const router = useRouter()
const store = useStore()
const SHANGHAI_TIMEZONE = 'Asia/Shanghai'
const FAMILY_COVER_IMAGES = [familyCover1, familyCover2, familyCover3]

const families = ref([])
const items = ref([])
const members = ref([])
const selectedFamilyId = ref('')
const managingFamily = ref(null)
const showMembersPanel = ref(false)
const showItemModal = ref(false)
const showFamilyModal = ref(false)
const showDeleteItemConfirm = ref(false)
const showDeleteFamilyConfirm = ref(false)
const showRemoveMemberConfirm = ref(false)
const isLoadingFamilies = ref(false)
const isLoadingItems = ref(false)
const isLoadingMembers = ref(false)
const isSubmittingItem = ref(false)
const isCreatingFamily = ref(false)
const isDeletingItem = ref(false)
const isRemovingMember = ref(false)
const isDeletingFamilyId = ref('')
const isManagingFamilyId = ref('')
const activeFamilyMenuId = ref('')
const itemForm = ref(createEmptyItemForm())
const familyForm = ref(createEmptyFamilyForm())
const deletingItem = ref(null)
const deletingFamily = ref(null)
const removingMember = ref(null)

const currentUserId = computed(() => store.state.userInfo?.id || '')
const selectedFamily = computed(() => families.value.find((family) => family.id === selectedFamilyId.value) || null)
const filteredItems = computed(() => items.value.filter((item) => item.family_id === selectedFamilyId.value))

onMounted(async () => {
  document.addEventListener('click', handleDocumentClick)
  await loadFamilies()
  if (selectedFamilyId.value) {
    await loadItems()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})

function createEmptyItemForm() {
  return {
    id: '',
    name: '',
    description: '',
    location: '',
    expiration_date: ''
  }
}

function createEmptyFamilyForm() {
  return {
    name: ''
  }
}

async function refreshAll() {
  await loadFamilies()
  if (selectedFamilyId.value) {
    await loadItems()
  }
}

async function loadFamilies() {
  isLoadingFamilies.value = true
  try {
    const response = await request.get('/user/families')
    families.value = Array.isArray(response) ? response : []

    if (families.value.length === 0) {
      selectedFamilyId.value = ''
      return
    }

    const hasSelected = families.value.some((family) => family.id === selectedFamilyId.value)
    if (!hasSelected) {
      const defaultFamily = families.value.find((family) => family.is_default)
      selectedFamilyId.value = (defaultFamily || families.value[0]).id
    }
  } catch (error) {
    console.error('Failed to load families:', error)
    families.value = []
    selectedFamilyId.value = ''
  } finally {
    isLoadingFamilies.value = false
  }
}

function openFamilyModal() {
  familyForm.value = createEmptyFamilyForm()
  showFamilyModal.value = true
}

function closeFamilyModal() {
  showFamilyModal.value = false
  familyForm.value = createEmptyFamilyForm()
}

async function submitFamily() {
  const name = familyForm.value.name.trim()

  if (!name) {
    message.warning('请先填写家庭名称')
    return
  }

  isCreatingFamily.value = true
  try {
    const created = await request.post('/user/families', { name })
    message.success('家庭创建成功')
    closeFamilyModal()
    await loadFamilies()

    if (created?.id) {
      selectedFamilyId.value = created.id
      await loadItems()
    }
  } catch (error) {
    console.error('Failed to create family:', error)
  } finally {
    isCreatingFamily.value = false
  }
}

async function loadItems() {
  if (!selectedFamilyId.value) {
    items.value = []
    return
  }

  isLoadingItems.value = true
  try {
    const response = await request.get('/item/items')
    items.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to load items:', error)
    items.value = []
  } finally {
    isLoadingItems.value = false
  }
}

async function selectFamily(familyId) {
  activeFamilyMenuId.value = ''
  if (familyId === selectedFamilyId.value) {
    return
  }

  selectedFamilyId.value = familyId
  await loadItems()
}

function toggleFamilyMenu(familyId) {
  activeFamilyMenuId.value = activeFamilyMenuId.value === familyId ? '' : familyId
}

function handleDocumentClick() {
  activeFamilyMenuId.value = ''
}

async function setDefaultFamily(family) {
  if (family.is_default) {
    activeFamilyMenuId.value = ''
    return
  }

  try {
    await request.put(`/user/families/default/${family.id}`)
    message.success('默认家庭已更新')
    selectedFamilyId.value = family.id
    activeFamilyMenuId.value = ''
    await loadFamilies()
    await loadItems()
  } catch (error) {
    console.error('Failed to set default family:', error)
  }
}

async function removeFamily(family) {
  activeFamilyMenuId.value = ''
  deletingFamily.value = family
  showDeleteFamilyConfirm.value = true
}

function closeDeleteFamilyConfirm(force = false) {
  if (!force && isDeletingFamilyId.value) {
    return
  }

  showDeleteFamilyConfirm.value = false
  deletingFamily.value = null
}

async function confirmDeleteFamily() {
  if (!deletingFamily.value) {
    return
  }

  isDeletingFamilyId.value = deletingFamily.value.id
  try {
    await request.delete(`/user/families/${deletingFamily.value.id}`)
    message.success('家庭删除成功')
    if (managingFamily.value?.id === deletingFamily.value.id) {
      closeMembersPanel()
    }
    closeDeleteFamilyConfirm(true)
    await loadFamilies()
    await loadItems()
  } catch (error) {
    console.error('Failed to delete family:', error)
  } finally {
    isDeletingFamilyId.value = ''
  }
}

async function openMembersPanel(family) {
  activeFamilyMenuId.value = ''
  managingFamily.value = family
  showMembersPanel.value = true
  isManagingFamilyId.value = family.id
  await loadMembers(family.id)
  isManagingFamilyId.value = ''
}

function closeMembersPanel() {
  showMembersPanel.value = false
  managingFamily.value = null
  members.value = []
}

async function loadMembers(familyId) {
  isLoadingMembers.value = true
  try {
    const response = await request.get('/user/families/members', {
      params: { family_id: familyId }
    })
    members.value = Array.isArray(response) ? response : []
  } catch (error) {
    console.error('Failed to load family members:', error)
    members.value = []
  } finally {
    isLoadingMembers.value = false
  }
}

async function changeMemberRole(member, event) {
  const nextRole = event.target.value
  if (!managingFamily.value || nextRole === member.role) {
    return
  }

  try {
    await request.put('/user/families/members/role', {
      family_id: managingFamily.value.id,
      member_id: member.id,
      role: nextRole
    })
    message.success('成员角色已更新')
    await Promise.all([loadMembers(managingFamily.value.id), loadFamilies()])
  } catch (error) {
    console.error('Failed to update member role:', error)
    event.target.value = member.role
  }
}

async function removeMember(member) {
  if (!managingFamily.value) {
    return
  }

  removingMember.value = member
  showRemoveMemberConfirm.value = true
}

function closeRemoveMemberConfirm(force = false) {
  if (!force && isRemovingMember.value) {
    return
  }

  showRemoveMemberConfirm.value = false
  removingMember.value = null
}

async function confirmRemoveMember() {
  if (!managingFamily.value || !removingMember.value) {
    return
  }

  isRemovingMember.value = true
  try {
    await request.delete('/user/families/members', {
      data: {
        family_id: managingFamily.value.id,
        member_id: removingMember.value.id
      }
    })
    message.success('成员已移出家庭')
    closeRemoveMemberConfirm(true)
    await loadMembers(managingFamily.value.id)
  } catch (error) {
    console.error('Failed to remove member:', error)
  } finally {
    isRemovingMember.value = false
  }
}

function openItemModal(item) {
  itemForm.value = item
    ? {
        id: item.id || '',
        name: item.name || '',
        description: item.description || '',
        location: item.location || '',
        expiration_date: toDatetimeLocal(item.expiration_date)
      }
    : createEmptyItemForm()
  showItemModal.value = true
}

function closeItemModal() {
  showItemModal.value = false
  itemForm.value = createEmptyItemForm()
}

async function submitItem() {
  if (!selectedFamily.value) {
    return
  }

  if (!itemForm.value.name || !itemForm.value.location) {
    message.warning('请至少填写物资名称和存放位置')
    return
  }

  const payload = {
    name: itemForm.value.name,
    description: itemForm.value.description || null,
    location: itemForm.value.location,
    family_id: selectedFamily.value.id,
    expiration_date: normalizeDatetime(itemForm.value.expiration_date)
  }

  isSubmittingItem.value = true
  try {
    if (itemForm.value.id) {
      await request.put(`/item/items/${itemForm.value.id}`, {
        name: payload.name,
        description: payload.description,
        location: payload.location,
        expiration_date: payload.expiration_date
      })
      message.success('物资更新成功')
    } else {
      await request.post('/item/items', payload)
      message.success('物资添加成功')
    }
    closeItemModal()
    await loadItems()
  } catch (error) {
    console.error('Failed to submit item:', error)
  } finally {
    isSubmittingItem.value = false
  }
}

function deleteItem(item) {
  deletingItem.value = item
  showDeleteItemConfirm.value = true
}

function closeDeleteItemConfirm(force = false) {
  if (!force && isDeletingItem.value) {
    return
  }

  showDeleteItemConfirm.value = false
  deletingItem.value = null
}

async function confirmDeleteItem() {
  if (!deletingItem.value) {
    return
  }

  isDeletingItem.value = true
  try {
    await request.delete(`/item/items/${deletingItem.value.id}`)
    message.success('物资删除成功')
    closeDeleteItemConfirm(true)
    await loadItems()
  } catch (error) {
    console.error('Failed to delete item:', error)
  } finally {
    isDeletingItem.value = false
  }
}

function normalizeDatetime(value) {
  if (!value) {
    return null
  }

  const match = String(value).match(/^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2})?$/)
  if (!match) {
    return null
  }

  return `${match[1]} ${match[2]}:00`
}

function toDatetimeLocal(value) {
  const parts = getShanghaiDateParts(value)
  if (!parts) {
    return ''
  }

  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

function formatDate(value) {
  const parts = getShanghaiDateParts(value)
  if (!parts) {
    return '-'
  }

  return `${parts.year}/${parts.month}/${parts.day} ${parts.hour}:${parts.minute}`
}

function getShanghaiDateParts(value) {
  if (!value) {
    return null
  }

  const text = String(value).trim()
  const plainMatch = text.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?$/)
  if (plainMatch) {
    return {
      year: plainMatch[1],
      month: plainMatch[2],
      day: plainMatch[3],
      hour: plainMatch[4],
      minute: plainMatch[5]
    }
  }

  const date = new Date(text)
  if (Number.isNaN(date.getTime())) {
    return null
  }

  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: SHANGHAI_TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
  const parts = formatter.formatToParts(date)
  const lookup = Object.fromEntries(parts.filter((part) => part.type !== 'literal').map((part) => [part.type, part.value]))

  return {
    year: lookup.year,
    month: lookup.month,
    day: lookup.day,
    hour: lookup.hour,
    minute: lookup.minute
  }
}

function handleLogout() {
  store.commit('CLEAR_TOKEN')
  router.push('/')
  message.success('已退出登录')
}

function getFamilyCoverStyle(index) {
  const coverImage = FAMILY_COVER_IMAGES[index % FAMILY_COVER_IMAGES.length]

  return {
    backgroundImage: `linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.18)), url("${coverImage}")`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }
}
</script>

<style scoped>
.mgmt-page {
  min-height: 100vh;
  display: flex;
  background: #fdfbf9;
  color: #374151;
  font-family: 'Inter', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

.icon-img {
  width: 22px;
  height: 22px;
  display: block;
}

.icon-lg {
  width: 28px;
  height: 28px;
}

.mgmt-sidebar {
  width: 80px;
  background: #ffffff;
  border-right: 1px solid #f3f4f6;
  padding: 32px 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
}

.sidebar-top {
  display: flex;
  flex-direction: column;
  gap: 32px;
  align-items: center;
}

.home-button {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(212, 176, 140, 0.1);
  margin-bottom: 40px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.nav-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon {
  border: 0;
  background: transparent;
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
  text-decoration: none;
}

.nav-icon:hover,
.nav-icon.active {
  background: rgba(212, 176, 140, 0.1);
}

.nav-tooltip {
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%) translateX(-8px);
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
  background: #ffffff;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
  color: #6b7280;
  font-size: 12px;
  line-height: 1;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 20;
}

.nav-trigger:hover .nav-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.sidebar-bottom {
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
  padding-bottom: 4px;
}

.logout-trigger,
.settings-trigger {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logout-btn,
.settings-btn {
  border: 0;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.logout-btn:hover,
.settings-btn:hover {
  background: rgba(212, 176, 140, 0.1);
}

.logout-btn .icon-img,
.settings-btn .icon-img {
  width: 20px;
  height: 20px;
}

.logout-tooltip,
.settings-tooltip {
  position: absolute;
  left: calc(100% + 12px);
  top: 50%;
  transform: translateY(-50%) translateX(-8px);
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid #f3f4f6;
  background: #ffffff;
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
  color: #6b7280;
  font-size: 12px;
  line-height: 1;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 20;
}

.logout-trigger:hover .logout-tooltip,
.settings-trigger:hover .settings-tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

.mgmt-main {
  flex: 1;
  min-width: 0;
  padding: 28px 34px;
  display: grid;
  gap: 18px;
}

.mgmt-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.mgmt-header h1 {
  margin: 0;
  font-size: 28px;
  color: #1f2937;
}

.mgmt-header p {
  margin: 8px 0 0;
  color: #9ca3af;
  font-size: 13px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 8px 12px;
  background: #fcf8f3;
  color: #b1865b;
  font-size: 12px;
  border: 1px solid rgba(212, 176, 140, 0.35);
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.family-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 14px;
}

.family-card {
  border: 1px solid #f3ece4;
  background: linear-gradient(180deg, #ffffff 0%, #fcfaf7 100%);
  border-radius: 18px;
  padding: 0;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  overflow: visible;
  position: relative;
}

.family-card:hover,
.family-card.active {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  border-color: rgba(212, 176, 140, 0.5);
}

.family-cover {
  height: 148px;
  position: relative;
  border-bottom: 1px solid #f3ece4;
  overflow: hidden;
  border-top-left-radius: 18px;
  border-top-right-radius: 18px;
}

.family-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.12) 45%, rgba(255,255,255,0.78) 100%);
}

.cover-leaf {
  position: absolute;
  z-index: 1;
  color: rgba(212, 176, 140, 0.6);
  font-size: 20px;
}

.leaf-left {
  left: 16px;
  bottom: 12px;
}

.leaf-right {
  right: 16px;
  top: 14px;
}

.family-card-body {
  padding: 16px;
  position: relative;
  z-index: 2;
}

.family-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  position: relative;
}

.family-title-wrap {
  min-width: 0;
}

.family-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.family-card h3 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.family-meta {
  margin: 8px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: #6b7280;
}

.family-desc {
  margin-top: 14px;
  border-radius: 12px;
  border: 1px solid #f3ece4;
  background: #ffffff;
  color: #8f6746;
  font-size: 13px;
  text-align: center;
  padding: 14px 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
}

.badge-default {
  background: rgba(212, 176, 140, 0.16);
  color: #8f6746;
}

.badge-owner {
  background: #eff6ff;
  color: #1d4ed8;
}

.family-menu-wrap {
  position: relative;
  flex-shrink: 0;
}

.menu-trigger {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.menu-trigger:hover {
  background: rgba(15, 23, 42, 0.05);
}

.menu-trigger .icon-img {
  width: 18px;
  height: 18px;
}

.family-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 170px;
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.12);
  padding: 8px;
  display: grid;
  gap: 4px;
  z-index: 40;
}

.family-menu-item {
  width: 100%;
  border: 0;
  background: transparent;
  text-align: left;
  border-radius: 10px;
  padding: 10px 12px;
  color: #4b5563;
  font-size: 13px;
}

.family-menu-item:hover {
  background: #fafafa;
}

.family-menu-item.danger {
  color: #dc2626;
}

.table-wrap {
  overflow-x: auto;
}

.inventory-table {
  width: 100%;
  border-collapse: collapse;
}

.inventory-table th,
.inventory-table td {
  padding: 14px 12px;
  text-align: left;
  border-bottom: 1px solid #f3f4f6;
  font-size: 13px;
  vertical-align: top;
}

.inventory-table th {
  color: #9ca3af;
  font-weight: 600;
  font-size: 12px;
}

.inventory-table td {
  color: #374151;
}
.row-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.member-list {
  display: grid;
  gap: 10px;
}

.member-card {
  border: 1px solid #f3f4f6;
  border-radius: 14px;
  padding: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.member-card strong {
  display: block;
  font-size: 14px;
  color: #1f2937;
}

.member-card p {
  margin: 6px 0 0;
  color: #9ca3af;
  font-size: 12px;
}

.member-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.member-actions select,
.item-form :deep(input),
.item-form :deep(textarea) {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 11px 12px;
  font-size: 14px;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
}

.member-actions select:focus,
.item-form :deep(input:focus),
.item-form :deep(textarea:focus) {
  border-color: #d4b08c;
  box-shadow: 0 0 0 3px rgba(212, 176, 140, 0.14);
}

.item-form {
  display: grid;
  gap: 14px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.item-form .form-actions {
  justify-content: center;
  align-items: center;
}

@media (min-width: 1024px) {
  .mgmt-sidebar {
    width: 96px;
  }
}

@media (max-width: 1024px) {
  .mgmt-sidebar {
    width: 72px;
  }

  .mgmt-main {
    padding: 20px;
  }

  .family-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }

  .mgmt-header,
  .panel-head-with-actions,
  .member-card {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .mgmt-page {
    flex-direction: column;
  }

  .mgmt-main {
    padding: 16px;
  }

  .mgmt-header,
  .header-actions,
  .panel-actions,
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .family-card-top,
  .member-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .family-menu {
    left: 0;
    right: auto;
  }

}
</style>
