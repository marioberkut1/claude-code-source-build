import { parseFrontmatter } from '../../utils/frontmatterParser.js'
import { registerBundledSkill } from '../bundledSkills.js'
import skillMd from './i-have-adhd/SKILL.md'

const { content: SKILL_BODY } = parseFrontmatter(skillMd)

// Adapted from https://github.com/ayghri/i-have-adhd (MIT license).
export function registerIHaveAdhdSkill(): void {
  registerBundledSkill({
    name: 'i-have-adhd',
    description:
      'Shape output for a reader with ADHD: lead with the next action, number multi-step work, restate state across turns, suppress tangents, give specific time estimates, make wins visible. Invoke with /i-have-adhd; stays on until "stop adhd mode".',
    disableModelInvocation: true,
    userInvocable: true,
    async getPromptForCommand(args) {
      const parts: string[] = [SKILL_BODY.trimStart()]
      if (args) {
        parts.push(`## User Request\n\n${args}`)
      }
      return [{ type: 'text', text: parts.join('\n\n') }]
    },
  })
}
