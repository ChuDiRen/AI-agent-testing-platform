你是一个资深的java专家，请在开发中遵循如下规则：
- 严格遵循 **SOLID、DRY、KISS、YAGNI** 原则
- 遵循 **OWASP 安全最佳实践**（如输入验证、SQL注入防护）
- 采用 **分层架构设计**，确保职责分离
- 代码变更需通过 **单元测试覆盖**（测试覆盖率 ≥ 80%）

---

## 二、技术栈规范
### 技术栈要求
- **框架**：Spring Boot 3.x + Java 17
- **依赖**：
  - 核心：Spring Web, Spring Data JPA, Lombok
  - 数据库：PostgreSQL Driver 或其他关系型数据库驱动
  - 其他：Swagger (SpringDoc), Spring Security (如需权限控制)

---

## 三、应用逻辑设计规范
### 1. 分层架构原则
| 层级          | 职责                                                                 | 约束条件                                                                 |
|---------------|----------------------------------------------------------------------|--------------------------------------------------------------------------|
| **Controller** | 处理 HTTP 请求与响应，定义 API 接口                                 | - 禁止直接操作数据库<br>- 必须通过 Service 层调用                          |
| **Service**    | 业务逻辑实现，事务管理，数据校验                                   | - 必须通过 Repository 访问数据库<br>- 返回 DTO 而非实体类（除非必要）       |
| **Repository** | 数据持久化操作，定义数据库查询逻辑                                 | - 必须继承 `JpaRepository`<br>- 使用 `@EntityGraph` 避免 N+1 查询问题       |
| **Entity**     | 数据库表结构映射对象                                               | - 仅用于数据库交互<br>- 禁止直接返回给前端（需通过 DTO 转换）               |

---

## 四、核心代码规范
### 1. 实体类（Entity）规范
```java
@Entity
@Data // Lombok 注解
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 50)
    private String username;

    @Email
    private String email;

    // 关联关系使用懒加载
    @ManyToOne(fetch = FetchType.LAZY)
    private Department department;
}
```

### 2. 数据访问层（Repository）规范
```java
public interface UserRepository extends JpaRepository<User, Long> {
    // 命名查询
    Optional<User> findByUsername(String username);

    // 自定义 JPQL 查询
    @Query("SELECT u FROM User u JOIN FETCH u.department WHERE u.id = :id")
    @EntityGraph(attributePaths = {"department"})
    Optional<User> findUserWithDepartment(@Param("id") Long id);
}
```

### 3. 服务层（Service）规范
```java
@Service
public class UserServiceImpl implements UserService {
    @Autowired
    private UserRepository userRepository;

    @Transactional
    public ApiResponse<UserDTO> createUser(UserDTO dto) {
        // 业务逻辑实现
        User user = User.builder().username(dto.getUsername()).build();
        User savedUser = userRepository.save(user);
        return ApiResponse.success(UserDTO.fromEntity(savedUser));
    }
}
```

### 4. 控制器（RestController）规范
```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping
    public ResponseEntity<ApiResponse<UserDTO>> createUser(@RequestBody @Valid UserDTO dto) {
        try {
            ApiResponse<UserDTO> response = userService.createUser(dto);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return GlobalExceptionHandler.errorResponseEntity(e.getMessage(), HttpStatus.BAD_REQUEST);
        }
    }
}
```

---

## 五、数据传输对象（DTO）规范
```java
// 使用 record 或 @Data 注解
public record UserDTO(
    @NotBlank String username,
    @Email String email
) {
    public static UserDTO fromEntity(User entity) {
        return new UserDTO(entity.getUsername(), entity.getEmail());
    }
}
```

---

## 六、全局异常处理规范
### 1. 统一响应类（ApiResponse）
```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ApiResponse<T> {
    private String result; // SUCCESS/ERROR
    private String message;
    private T data;

    // 工厂方法
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>("SUCCESS", "操作成功", data);
    }

    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>("ERROR", message, null);
    }
}
```

### 2. 全局异常处理器（GlobalExceptionHandler）
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ApiResponse<?>> handleEntityNotFound(EntityNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(ApiResponse.error(ex.getMessage()));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiResponse<?>> handleValidationErrors(MethodArgumentNotValidException ex) {
        String errorMessage = ex.getBindingResult()
            .getFieldErrors()
            .stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.joining(", "));
        return ResponseEntity.badRequest().body(ApiResponse.error(errorMessage));
    }
}
```

---

## 七、安全与性能规范
1. **输入校验**：
   - 使用 `@Valid` 注解 + JSR-303 校验注解（如 `@NotBlank`, `@Size`）
   - 禁止直接拼接 SQL 防止注入攻击
2. **事务管理**：
   - `@Transactional` 注解仅标注在 Service 方法上
   - 避免在循环中频繁提交事务
3. **性能优化**：
   - 使用 `@EntityGraph` 预加载关联关系
   - 避免在循环中执行数据库查询（批量操作优先）

---

## 八、代码风格规范
1. **命名规范**：
   - 类名：`UpperCamelCase`（如 `UserServiceImpl`）
   - 方法/变量名：`lowerCamelCase`（如 `saveUser`）
   - 常量：`UPPER_SNAKE_CASE`（如 `MAX_LOGIN_ATTEMPTS`）
2. **注释规范**：
   - 方法必须添加注释且方法级注释使用 Javadoc 格式
   - 计划待完成的任务需要添加 `// TODO` 标记
   - 存在潜在缺陷的逻辑需要添加 `// FIXME` 标记
3. **代码格式化**：
   - 使用 IntelliJ IDEA 默认的 Spring Boot 风格
   - 禁止手动修改代码缩进（依赖 IDE 自动格式化）

---

## 九、部署规范
1. **部署规范**：
   - 生产环境需禁用 `@EnableAutoConfiguration` 的默认配置
   - 敏感信息通过 `application.properties` 外部化配置
   - 使用 `Spring Profiles` 管理环境差异（如 `dev`, `prod`）

---

## 十、扩展性设计规范
1. **接口优先**：
   - 服务层接口（`UserService`）与实现（`UserServiceImpl`）分离
2. **扩展点预留**：
   - 关键业务逻辑需提供 `Strategy` 或 `Template` 模式支持扩展
3. **日志规范**：
   - 使用 `SLF4J` 记录日志（禁止直接使用 `System.out.println`）
   - 核心操作需记录 `INFO` 级别日志，异常记录 `ERROR` 级别
```