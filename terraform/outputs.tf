output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_host" {
  description = "RDS instance host (without port)"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "Database port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "Database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_username" {
  description = "Database username"
  value       = aws_db_instance.postgres.username
  sensitive   = true
}

output "rds_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.postgres.arn
}

output "security_group_id" {
  description = "Security group ID"
  value       = aws_security_group.rds_sg.id
}

output "connection_string" {
  description = "Database connection details"
  value = <<-EOT
DB_HOST=${aws_db_instance.postgres.address}
DB_PORT=${aws_db_instance.postgres.port}
DB_NAME=${aws_db_instance.postgres.db_name}
DB_USER=${aws_db_instance.postgres.username}
DB_PASSWORD=${var.db_password}
  EOT
  sensitive = true
}
